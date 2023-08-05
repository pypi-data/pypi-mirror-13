""" Implement an OA client according to communication protocol
with scifloware specifications to communicate with OAServers.
"""

from os.path import exists
from time import sleep

from .json_tools import post_json, wait_for_content


class OAClient(object):
    """ object used to encapsulate communication with OA server
    """
    def __init__(self):
        """ Constructor
        """
        self.compute_url = None
        self.ping_url = None
        self.delete_url = None

    def connect(self, oas):
        """Connect the client to a given OA server.

        args:
         - oas (OAServer): server to connect to

        return:
         - (bool): whether connection is successful or not
        """
        oas.register("reg.json")
        oas.start()

        ans = wait_for_content("reg.json")
        self.compute_url = ans['args']['url']
        self.ping_url = ans['args']['urlping']
        self.delete_url = ans['args']['urldelete']

        return True

    def ping(self):
        """Ping associated server and return server state.

        return:
         - (str): current server state
        """
        cmd = dict(url="pingans.json")
        post_json(self.ping_url, cmd)
        ans = wait_for_content("pingans.json")

        return ans['state']

    def compute_script(self, pycode, data, url_return):
        """Launch execution of pycode on server.

        .. note:: function return once computation is launched but not
                  necessarily finished

        args:
         - pycode (str): python code to execute,
                         must contain some main function
         - data (dict of str, any): data to send to the script
         - url_return (str): url where oas will write result of computation
        """
        data_str = "\n".join("%s = %s" % it for it in data.items())
        cmd = dict(workflow="pycode:" + pycode,
                   urldata=data_str,
                   urlreturn=url_return)
        post_json(self.compute_url, cmd)

        while exists(self.compute_url):
            sleep(0.1)
