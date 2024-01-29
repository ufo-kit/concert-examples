"""# *uca_remote_walker* session manual

## Notes
This session demonstrates combining the remote directory walker api and the
live view session to write the data sent from camera while viewing the same
live. For this experiment we would use the ucad mock plugin. This means
running this experiment needs some preparations, which are described as follows.

###############################################################################
1. Ensure that libuca[https://github.com/ufo-kit/libuca.git] and 
uca-net[https://github.com/ufo-kit/uca-net.git] packages are installed, so that
`ucad mock` command can be triggered from a separate console. This runs a mock
camera server in the background on default port `8989`. It is advised to set
the G_MESSAGES_DEBUG environment variable to the value 'all' before running
`ucad mock` to see the debug log messages from libuca in the console.

2. The Tango walker device server must be executed on another console with
the command `concert tango walker --loglevel debug --port 7001`, which runs
a Tango device server that points to $HOME directory by default. Furthermore,
the `root` directory must be set in the session to point the walker device
server to the correct location to write to.

3. Run the session and execute,
    i) await camera.start_recording() # transitions the camera from 'standby' -> 'recording'
    ii) write = walker.write_sequence(root) # specifies where the data to be written
    iii) await camera.grab_many(100) # send request to camera server to stream frames
###############################################################################

This session works with the decentralized implementation of data
acquisition. The walker is a tango device server which is also a ZMQ Receiver
expecting to receive frames from the camera server on a reliable socket connection.
Viewer on the other hand is just a ZMQ Receiver live view endpoint which consumes
the incoming frames on an unreliable socket connection. In the session we register
both receiver endpoints onto the remote network camera server, which streams mock
data frames. Unlike the `remote_experiment` session in this session we explicitly
set the camera transition from the state 'standby' -> 'recording' and instruct
the walker api to listen to its receiver endpoint for incoming frames and write
it before explicitly requesting the camera server to stream 100 frames using
`grab_many`.
"""
import logging
import os
from typing import Dict
import zmq
import concert
from concert.quantities import q
from concert.networking.base import get_tango_device
from concert.experiments.addons import tango as tng
from concert.ext.viewers import PyQtGraphViewer
from concert.devices.cameras.uca import RemoteNetCamera
from concert.experiments.dummy import ImagingExperiment
from concert.loghandler import RemoteLoggingHandler
from concert.storage import RemoteDirectoryWalker
from concert.typing import RemoteDirectoryWalkerTangoDevice
from utils import CommData

# Define logger
LOG = logging.getLogger(__name__)

# Setting the ucad parameters. With the 'ucad mock' running locally we specify
# the host and port for the mocked camera server. To make it work we do the
# following in a separate terminal window having the libuca and uca-net built
# in the environment.
# Enable debug logs: export `export G_MESSAGES_DEBUG=all`
# Run mock camera server with debug logging: `ucad mock`
os.environ['UCA_NET_HOST'] = "localhost"
os.environ['UCA_NET_PORT'] = "8989"

# Specifying a directory to write to
root = "[Set valid root directory where the experiment data must be written]"

# Specifying the socket connection endpoints for zmq streams,
## 1. walker: uses zmq.PUSH type socket to ensure reliable connection for
## writing data.
## 2. viewer: relies on zmq.PUB type socket because it can function on
## unreliable connection.
comms: Dict[str, CommData] = {
        "walker": CommData("localhost", 8996, socket_type=zmq.PUSH),
        "viewer": CommData("localhost", 8995, socket_type=zmq.PUB)
}

# Specifying the uri where the tango device is running. The port 7001 is the
# tango port for the walker and writer device server. It has no connection
# with zmq.
walker_dev_uri = f"{os.uname()[1]}:7001/concert/tango/walker#dbase=no"

# Instantiate remote walker api which internally refers to the tango device
# running at port 7001 in this example.
walker_dev: RemoteDirectoryWalkerTangoDevice = get_tango_device(
        uri=walker_dev_uri, timeout=1000 * q.s)
## Since the underlying tango device server is also a ZMQ stream listener
## in the background we register its receiving endpoint i.e., client end of the
## socket connection between walker and camera server.
await walker_dev.write_attribute("endpoint", comms["walker"].client_endpoint)
walker = await RemoteDirectoryWalker(device=walker_dev,root=root,
                                     bytes_per_file=2**40)

## Get logging handler and add to logger. We need to mindfully close the handler
## to actually get the logging done.
handler: RemoteLoggingHandler = await walker.get_log_handler()
LOG.addHandler(handler)

# Instantiate a remote network camera which relies on a camera server running in
# the background. That camera server is `ucad` uca daemon (running locally in
# this example on localhost:8989).
camera = await RemoteNetCamera()
LOG.info(f"instantiated camera with parameters:")
LOG.info(await camera.info_table)

# Register the destination socket endpoints for the camera server. These
# registered endpoints, namely walker server and viewer server are the targets
# of the camera streams.
for comm in comms.values():
    try:
        await camera.register_endpoint(comm.server_endpoint, comm.socket_type,
                                       sndhwm=comm.sndhwm)
        LOG.info(f"registered server endpoint: {comm.server_endpoint} to camera")
    except Exception as e:
        LOG.warning(f"registering endpoint {comm.server_endpoint} unsuccessful - retrying")
        print(f'Retrying registration: {comm.server_endpoint}')
        await camera.unregister_endpoint(comm.server_endpoint)
        await camera.register_endpoint(comm.server_endpoint, comm.socket_type)

# Define viewer object and and let it subscribe to the client endpoint which is
# its end of the PUB-SUB socket connection between viewer and camera server.
viewer = await PyQtGraphViewer()
viewer.subscribe(comms["viewer"].client_endpoint)
LOG.info(f"registered client endpoint: {comms['viewer'].client_endpoint} for live view")

# Detach and close the handler
LOG.removeHandler(handler)
await handler.aclose()

