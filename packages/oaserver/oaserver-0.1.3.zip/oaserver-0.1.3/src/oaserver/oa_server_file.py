""" REST implementation of OA server
"""

import os
import threading
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .oa_server import OAServer
from .json_tools import get_json, post_json, URLError


class OAServerFile(FileSystemEventHandler):
    """ File front end for OA server.

    Use file system to communicate with the OAServer
    """
    def __init__(self, sid, wpth):
        """ Constructor

        args:
         - sid (str): unique id for this server.
         - wpth (str): path, directory to watch for commands
        """
        FileSystemEventHandler.__init__(self)
        self._oas = OAServer(sid)

        if not os.path.exists(wpth):
            raise UserWarning("Watched path does not exists: '%s'" % wpth)

        self._obs = Observer()
        self._obs.schedule(self, wpth)
        # self._obs.start()

        # register
        self._compute_pth = os.path.join(wpth, "compute.cmd")
        self._ping_pth = os.path.join(wpth, "ping.cmd")
        self._delete_pth = os.path.join(wpth, "delete.cmd")

    #########################################################################
    #
    #   watchdog file observer interface
    #
    #########################################################################
    def start(self):
        self._obs.start()

    def stop(self):
        self._obs.stop()

    def join(self):
        self._obs.join()

    def on_created(self, event):
        if event.src_path == self._ping_pth:
            self.ping()
        elif event.src_path == self._compute_pth:
            self.compute()
        elif event.src_path == self._delete_pth:
            self.delete()
        else:
            if event.src_path.split(".")[-1] != "lock":
                print "created", event.src_path

    #########################################################################
    #
    #   OAServer interface wrappers
    #
    #########################################################################
    def ping(self):
        data = get_json(self._ping_pth)
        self._oas.ping(data['url'])
        os.remove(self._ping_pth)

    def compute(self):
        data = get_json(self._compute_pth)
        args = (data["workflow"],
                data["urldata"],
                data["urlreturn"])

        th = threading.Thread(group=None,
                              target=self._oas.compute,
                              name="OAS.compute",
                              args=args)
        th.start()
        os.remove(self._compute_pth)

    def delete(self):
        # data = read_json(self._delete_pth)
        self.stop()
        self._oas.delete()
        os.remove(self._delete_pth)

    #########################################################################
    #
    #   registration
    #
    #########################################################################
    def register(self, url_master):
        """ Register this worker server to a master.

        args:
         - url_master (str): url to use to register
        """
        data = {"type": "FileSystemEngine",  # fixed name for SFW protocol
                "args": {
                    "name": "OpenAlea",
                    "id": self._oas.server_id(),
                    "url": self._compute_pth,
                    "urlping": self._ping_pth,
                    "urldelete": self._delete_pth}
                }

        try:
            post_json(url_master, data)
        except URLError:
            raise UserWarning("unable to register with server")

        self._oas.registered()
