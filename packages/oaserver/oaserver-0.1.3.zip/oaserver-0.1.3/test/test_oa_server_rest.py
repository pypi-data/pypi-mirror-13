# from nose.tools import assert_raises
# import requests
# import requests_mock
# from time import sleep
#
# from oaserver.json_tools import post_json
# from oaserver.oa_server_rest import OAServerRest
#
#
# # def test_server_address_exists():
# #     sfws_descr = "127.0.0.1", 8082
# #     with requests_mock.Mocker() as m:
# #         m.post('http://%s:%d/init/CreateEngine/' % sfws_descr, text="toto")
# #
# #         assert_raises(UserWarning, lambda: OAServerRest("doofus",
# #                                                         ("127.0.0.1", 0),
# #                                                         sfws_descr))
#
#
# def test_server_register_correctly():
#     sfws_descr = "127.0.0.1", 8083
#     oas_descr = "127.0.0.1", 6543
#
#     assert_raises(UserWarning, lambda: OAServerRest("doofus",
#                                                     oas_descr,
#                                                     sfws_descr))
#
#     with requests_mock.Mocker() as m:
#         m.post('http://%s:%d/init/CreateEngine/' % sfws_descr,
#                text="toto",
#                status_code=404)
#
#         assert_raises(UserWarning, lambda: OAServerRest("doofus",
#                                                         oas_descr,
#                                                         sfws_descr))
#
#
# def test_server_is_working():
#     sfws_descr = "127.0.0.1", 8082
#     oas_descr = "127.0.0.1", 6540
#     semaphore = [True]
#
#     def create_callback(request, context):
#         resp = request.json()
#         print resp
#         assert resp['args']['id'] == "doofus"
#         assert resp['type'] == 'RestSystemEngine'
#
#     def ping_callback(request, context):
#         resp = request.json()
#         assert resp['id'] == "doofus"
#
#     def compute_callback(request, context):
#         resp = request.json()
#         assert resp['id'] == "doofus"
#         semaphore[0] = False
#
#     with requests_mock.Mocker(real_http=True) as m:
#         m.post('http://%s:%d/init/CreateEngine/' % sfws_descr,
#                text=create_callback)
#         m.post('http://%s:%d/PingAnswer/' % sfws_descr,
#                text=ping_callback)
#         m.post('http://%s:%d/ReturnAnswer/' % sfws_descr,
#                text=compute_callback)
#
#         # test registration
#         oas = OAServerRest("doofus", oas_descr, sfws_descr)
#         oas.start()
#
#         # test default
#         requests.get("http://%s:%d/helloworld/" % oas_descr)
#         requests.post("http://%s:%d/helloworld/" % oas_descr)
#
#         # test ping
#         data = {"url": 'http://%s:%d/PingAnswer/' % sfws_descr}
#         post_json("http://%s:%d/ping/" % oas_descr, data)
#
#         #test compute
#         data = {"workflow": "pycode:def main(): return 1",
#                 "urldata": "",
#                 "urlreturn": 'http://%s:%d/ReturnAnswer/' % sfws_descr}
#         post_json("http://%s:%d/compute/" % oas_descr, data)
#
#         # test delete
#         post_json("http://%s:%d/delete/" % oas_descr, {})
#
#         while semaphore[0]:
#             sleep(0.1)
#
#         oas.stop()
