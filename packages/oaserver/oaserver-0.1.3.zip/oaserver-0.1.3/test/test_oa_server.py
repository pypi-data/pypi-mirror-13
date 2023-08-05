import json
from nose.tools import assert_raises, with_setup
from os.path import join as pj
import requests_mock
# from time import sleep

from oaserver.json_tools import get_json
from oaserver.oa_server import OAServer

from .small_tools import ensure_created, rmdir

tmp_dir = "takapouet_compute"


def setup_func():
    ensure_created(tmp_dir)


def teardown_func():
    rmdir(tmp_dir)


pycode = """
from time import sleep

def main(a):
    print "pycode", a
    sleep(a)
    return a
"""


def test_server_id_can_be_anything():
    for sid in ("toto", 0, None):
        oas = OAServer(sid)
        assert oas.server_id() == sid

    oas = OAServer("toto")
    oas.set_server_id(1)
    assert oas.server_id() == 1


def test_server_id_cannot_change_once_registered():
    oas = OAServer(0)
    oas.registered()
    assert_raises(AssertionError, lambda: oas.set_server_id("toto"))


def test_server_state():
    oas = OAServer("toto")
    assert oas.state() == "created"

    oas.registered()
    assert oas.state() == "waiting"

    # oas.compute("pycode:from time import sleep\nsleep(0.1)", None, None)
    # oas.compute("dummy", 1, None)
    # assert oas.state() == "running"
    # sleep(0.2)
    # assert oas.state() == "waiting"


def test_server_ping():
    oas = OAServer("toto")

    def text_callback(request, context):
        del context
        resp = request.json()
        assert resp['id'] == "toto"
        assert resp['state'] == oas.state()

    with requests_mock.Mocker() as m:
        m.post('http://test.com/', text=text_callback)
        oas.ping('http://test.com/')


def test_server_ready_to_compute():
    oas = OAServer("toto")
    assert_raises(AssertionError, lambda: oas.compute("toto", "data", "ret"))


@with_setup(setup_func, teardown_func)
def test_server_compute_argument_definition():
    oas = OAServer("oas")
    oas.registered()

    def ru(workflow, url_data, url_return):
        assert_raises(UserWarning, lambda: oas.compute(workflow,
                                                       url_data,
                                                       url_return))

    # working components
    pyc = "pycode:def main():\n\tprint 1\n"
    dat = "a = 1"
    url_ret = pj(tmp_dir, "result.json")

    # workflow argument
    # completely wrong definition
    ru("toto", dat, url_ret)

    # bad pycode
    ru("pycode:", dat, url_ret)

    # bad dataflow
    # ru("dataflow:", "a=1", "http://return.com")

    # bad node id
    ru("toto:", dat, url_ret)
    ru(":toto", dat, url_ret)

    # url_data argument
    ru(pyc, "code:data", url_ret)
    ru(pyc, "file://data", url_ret)
    # ru("pycode:a=1", "http:data", "http://return.com")

    # url_return argument
    ru(pyc, dat, "ret")
    ru(pyc, dat, "file:ret")
    ru(pyc, dat, "http:ret")
    ru(pyc, dat, "http:/ret")


@with_setup(setup_func, teardown_func)
def test_server_compute_use_pycode_in_data():
    result_url = pj(tmp_dir, "result.json")
    oas = OAServer("oas")
    oas.registered()

    oas.compute("pycode:def main(a): return a", "a = 1", result_url)
    assert get_json(result_url) == dict(id='oas', result=1)

    oas.compute("pycode:def main(a): return a", "code:a = 2", result_url)
    assert get_json(result_url) == dict(id='oas', result=2)


@with_setup(setup_func, teardown_func)
def test_server_compute_use_local_in_data():
    result_url = pj(tmp_dir, "result.json")
    data_url = pj(tmp_dir, "data.json")
    oas = OAServer("oas")
    oas.registered()

    with open(data_url, 'w') as f:
        json.dump({'a': 3}, f)
    oas.compute("pycode:def main(a): return a",
                "file:%s" % data_url,
                result_url)
    assert get_json(result_url) == dict(id='oas', result=3)


@with_setup(setup_func, teardown_func)
def test_server_compute_use_remote_in_data():
    result_url = pj(tmp_dir, "result.json")
    data_url = "http://myserver.myns/data.json"
    oas = OAServer("oas")
    oas.registered()

    with requests_mock.Mocker() as m:
        m.get(data_url, text=json.dumps({'a': 4}))
        oas.compute("pycode:def main(a): return a", data_url, result_url)
        assert get_json(result_url) == dict(id='oas', result=4)


def test_server_compute_is_working():
    oas = OAServer("toto")
    oas.registered()

    def text_callback(request, context):
        del context
        resp = json.loads(request.text)
        assert resp["id"] == "toto"

    with requests_mock.Mocker() as m:
        m.post('http://test.com/return', text=text_callback)
        oas.compute("pycode:" + pycode, 'a=0.1', 'http://test.com/return')

        # with open("test/sample dataflow.py", 'r') as f:
        #     dataflow = f.read()
        #
        # oas.compute("dataflow:" + dataflow,
        #             "IN1=10\nIN2=12",
        #             'http://test.com/return')
        #
        # oas.compute("scifloware:simple_test",
        #             "a=10\nb=12",
        #             'http://test.com/return')


def test_server_delete():
    oas = OAServer("toto")
    oas.registered()

    oas.delete()
    assert oas.state() == "deleted"
