"""
Sends mosaik simulation data to ZeroMQ socket.

"""
import zmq
import mosaik_api

__version__ = '0.1'
meta = {
    'models': {
        'Socket': {
            'public': True,
            'any_inputs': True,
            'params': ['host', 'port', 'socket_type'],
            'attrs': [],
        },
    },
}


class MosaikZMQ(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta)
        self.sid = None
        self.eid = 'zmq_0'
        self.step_size = None
        self.duration = None
        self.db = None
        self.rels = None
        self.series = None
        self.data_buf = {}

        self.port = 5558
        self.host = 'tcp://*:'
        self.socket_type = 'PUB'

    def init(self, sid, step_size, duration):
        self.sid = sid
        self.step_size = step_size
        self.duration = duration
        return self.meta

    def create(self, num, model, host, port, socket_type, buf_size=1000, dataset_opts=None):
        if num != 1 or self.db is not None:
            raise ValueError('Can only create one zeromq socket.')
        if model != 'Socket':
            raise ValueError('Unknown model: "%s"' % model)

        self.context = zmq.Context()
        if socket_type == 'PUSH':
            self.sender = self.context.socket(zmq.PUSH)
        elif socket_type == 'PUB':
            self.sender = self.context.socket(zmq.PUB)
        else:
            raise ValueError('Unknown socket type. Allowed are PUSH and PUB')
        self.sender.bind(host + str(port))
        return [{'eid': self.eid, 'type': model, 'rel': []}]

    def step(self, time, inputs):
        assert len(inputs) == 1
        inputs.update({'timestamp': time})
        self.sender.send_json(inputs)
        return time + self.step_size

    def get_data(self, outputs):
        raise RuntimeError('mosaik_zmq does not provide any outputs.')


def main():
    desc = __doc__.strip()
    mosaik_api.start_simulation(MosaikZMQ(), desc)
