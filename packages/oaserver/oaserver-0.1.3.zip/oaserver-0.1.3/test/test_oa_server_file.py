import json
from nose.tools import assert_raises, with_setup
from os import remove
from os.path import exists
from os.path import join as pj
import requests_mock

from oaserver.json_tools import get_json, post_json, wait_for_content
from oaserver.oa_server_file import OAServerFile

from .small_tools import ensure_created, rmdir

tmp_dir = "takapouet_oasfile"
wdir = pj(tmp_dir, "watch")

NB = 50

def setup_func():
    ensure_created(tmp_dir)
    ensure_created(wdir)


def teardown_func():
    rmdir(tmp_dir)


def test_server_watch_path_exists():
    assert_raises(UserWarning, lambda: OAServerFile("doofus", "tooky"))


@with_setup(setup_func, teardown_func)
def test_server_register_correctly_locally():
    reg_file = pj(tmp_dir, "registration.json")
    oas = OAServerFile("doofus", wdir)
    oas.register(reg_file)

    assert exists(reg_file)
    reg = get_json(reg_file)
    for key in ('id', 'url', 'urlping', 'urldelete'):
        assert key in reg['args']


@with_setup(setup_func, teardown_func)
def test_server_register_correctly_when_started_already():
    reg_file = pj(tmp_dir, "registration.json")
    oas = OAServerFile("doofus", wdir)
    oas.start()
    oas.register(reg_file)

    assert exists(reg_file)
    reg = get_json(reg_file)
    for key in ('id', 'url', 'urlping', 'urldelete'):
        assert key in reg['args']

    oas.stop()


@with_setup(setup_func, teardown_func)
def test_server_register_correctly_remote():
    reg_url = "http://doofus.com/is/comming/for/you.json"
    oas = OAServerFile("doofus", wdir)

    def text_callback(request, context):
        reg = json.loads(request.text)
        for key in ('id', 'url', 'urlping', 'urldelete'):
            assert key in reg['args']

    with requests_mock.Mocker() as m:
        m.post(reg_url, text=text_callback)
        oas.register(reg_url)


@with_setup(setup_func, teardown_func)
def test_server_register_raise_error_if_not_registering():
    reg_url = "http://doofus.com/is/comming/for/you.json"
    oas = OAServerFile("doofus", wdir)

    with requests_mock.Mocker() as m:
        m.post(reg_url, text="", status_code=500)
        assert_raises(UserWarning, lambda: oas.register(reg_url))


@with_setup(setup_func, teardown_func)
def test_server_ping():
    answer_file = pj(tmp_dir, "answer.json")

    oas = OAServerFile("doofus", wdir)
    oas.start()
    oas.register(answer_file)

    ping_pth = get_json(answer_file)['args']['urlping']
    remove(answer_file)

    post_json(ping_pth, dict(url=answer_file))

    ans = wait_for_content(answer_file, NB)
    assert ans['state'] == 'waiting'
    assert ans['id'] == "doofus"

    oas.stop()
    oas.join()

    assert not exists(ping_pth)


@with_setup(setup_func, teardown_func)
def test_server_compute():
    answer_file = pj(tmp_dir, "answer.json")

    oas = OAServerFile("doofus", wdir)
    oas.start()
    oas.register(answer_file)

    cpt_pth = get_json(answer_file)['args']['url']
    remove(answer_file)

    post_json(cpt_pth, dict(workflow="pycode:def main(a): return a",
                            urldata="a = 1",
                            urlreturn=answer_file))

    ans = wait_for_content(answer_file, NB)
    assert ans['result'] == 1
    assert ans['id'] == "doofus"

    oas.stop()
    oas.join()

    assert not exists(cpt_pth)


@with_setup(setup_func, teardown_func)
def test_server_delete():
    answer_file = pj(tmp_dir, "answer.json")

    oas = OAServerFile("doofus", wdir)
    oas.start()
    oas.register(answer_file)

    del_pth = wait_for_content(answer_file, NB)['args']['urldelete']

    post_json(del_pth, dict())

    oas.join()

    assert not exists(del_pth)


pycode = """
from time import sleep

def main(a):
    sleep(a / 10.)
    return a
"""


@with_setup(setup_func, teardown_func)
def test_server_full_life():
    answer_file = pj(tmp_dir, "answer.json")

    oas = OAServerFile("doofus", wdir)
    oas.start()
    oas.register(answer_file)

    ans = wait_for_content(answer_file, NB)
    cpt_pth = ans['args']['url']
    ping_pth = ans['args']['urlping']
    del_pth = ans['args']['urldelete']

    for a in (1, 2):
        post_json(cpt_pth, dict(workflow="pycode:" + pycode,
                                urldata="a = %d" % a,
                                urlreturn=answer_file))

        answer_ping = pj(tmp_dir, "answer_ping.json")
        post_json(ping_pth, dict(url=answer_ping))
        ans = wait_for_content(answer_ping, NB)
        assert ans['id'] == "doofus"
        assert ans['state'] in ('running', 'waiting')

        ans = wait_for_content(answer_file, NB)
        assert ans['result'] == a
        assert ans['id'] == "doofus"

        answer_ping = pj(tmp_dir, "answer_ping.json")
        post_json(ping_pth, dict(url=answer_ping))
        ans = wait_for_content(answer_ping, NB)
        assert ans['id'] == "doofus"
        assert ans['state'] == 'waiting'

    post_json(del_pth, dict())

    oas.join()
