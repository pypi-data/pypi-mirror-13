from setuptools import setup

setup(
    name='mosaik-zmq',
	version='0.1.1',
	author='Jan Soeren Schwarz',
	author_email='schwarz at offis.de',
	description=('Sends mosaik simulation data to ZeroMQ socket.'),
	long_description=(open('README.txt').read() + '\n\n' +
                      open('CHANGES.txt').read() + '\n\n' +
                      open('AUTHORS.txt').read()),
    url='https://bitbucket.org/mosaik/mosaik-zmq',
	py_modules=['mosaik_zmq'],
    install_requires=[
        'pyzmq>=15.1.0',
        'mosaik-api>=2.1',
        'mosaik>=2.1'
    ],
    include_package_data = True,
    entry_points={
        'console_scripts': [
            'mosaik-zmq = mosaik_zmq:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering',
    ],
	)
