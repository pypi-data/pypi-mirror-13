""" REST implementation of OA server
"""

import threading
from urllib2 import URLError

from .json_tools import post_json, retrieve_json
from .oa_server import OAServer
from .threaded_server import ThreadedServer

oa_server = OAServer(None)


class OASDefault(object):
    """ Default task for openalea server
    """
    def GET(self):
        print "OAS received GET"

    def POST(self):
        print "OAS received POST"


class OASCompute(object):
    """ Task called to compute a dataflow
    """
    def POST(self):
        data = retrieve_json()
        args = (data["workflow"],
                data["urldata"],
                data["urlreturn"])

        th = threading.Thread(group=None,
                              target=oa_server.compute,
                              name="OAS.compute",
                              args=args)
        th.start()


class OASPing(object):
    """ Task called to ping state of server
    """
    def POST(self):
        data = retrieve_json()
        oa_server.ping(data['url'])


class OASDelete(object):
    """ Task called to compute a dataflow
    """
    def POST(self):
        oa_server.delete()


class OAServerRest(ThreadedServer):
    """ REST front end for OA server
    """
    def __init__(self, sid, oas_descr, sfws_descr):
        """ Constructor

        args:
         - sid (str): unique id for this server.
         - oas_descr (str,int): (address, port) of this server
         - sfws_descr (str,int): description of swf server to
                                 communicate with (address, port).
        """
        address, port = oas_descr
        urls = ('/helloworld/', 'OASDefault',
                '/compute/', 'OASCompute',
                '/ping/', 'OASPing',
                '/delete/', 'OASDelete')
        ThreadedServer.__init__(self, urls, globals(), address, port)

        oa_server.set_server_id(sid)

        # register
        base_url = "http://%s:%d/" % oas_descr
        data = {"type": "RestSystemEngine",  # fixed name for SFW protocol
                "args": {
                    "name": "OpenAlea",
                    "id": sid,
                    "url": base_url + "compute/",
                    "urlping": base_url + "ping/",
                    "urldelete": base_url + "delete/"}
                }

        url_register = "http://%s:%d/init/CreateEngine/" % sfws_descr
        try:
            post_json(url_register, data)
        except URLError:
            raise UserWarning("unable to register with scifloware server")

        oa_server.registered()
