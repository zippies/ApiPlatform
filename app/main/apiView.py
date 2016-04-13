# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify
from . import main
from .framework.objects import apilist,send_request,support_methods
import json

@main.route("/apis")
def showapi():
    return render_template("apis.html",apis=apilist,support_methods=support_methods)

@main.route("/testapi",methods=["POST"])
def testapi():
    info = {"result":True,"response":None,"errorMsg":None}
    method = request.form.get("method").lower()
    url = request.form.get("url")
    data = request.form.get("data")

    try:
        res = send_request("testapi",url=url,method=method,data=data)
        resp = {
            "statusCode":res.returncode,
            "elapsed":res.elapsed,
            "success":res.success,
            "errorMsg":res.errorMsg,
            "data":json.dumps(res.data,indent=4),
            "headers":dict(res.headers),
            "cookies":dict(res.cookies)
        }

        info["response"] = resp
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}

    return jsonify(info)

@main.route("/saveapi",methods=["POST"])
def saveapi():
    name = request.form.get("name")
    url = request.form.get("url")
    method = request.form.get("method")
    reqdata = request.form.get("reqdata")
    respdata = request.form.get("respdata")
    reqheader = request.form.get("reqheader")
    respheader = request.form.get("respheader")

    print(name,url,method,reqdata,respdata,reqheader,respheader)
    return "ok"


if __name__ == "__main__":
    app.run("0.0.0.0",port=9999)


# data = {
#     "cellphone":18516042356,
#     "password":"6547436690a26a399603a7096e876a2d"
# }
#
# headers = {
#     "token":""
# }
#
# res_login = request('login',data=data)
#
# if res_login.success:
#     headers["token"] = res_login.body.token
#
# res_stinfo = request("order_all",data={"pageSize":10,"page":1,"token":res_login.body.token},headers=headers)
#
# print(res_stinfo.url,res_stinfo.returncode)
# pprint(res_stinfo.data)



# login = api.login
# stinfo = api.getstudentinfo
# res_stinfo = None
# res_login = None
# print("[action]start request login:",login.url)
# if login.type == "get":
#     res_login = send_get('login', login.url, data=data)
# elif login.type == "post":
#     res_login = send_post('login',login.url,data=data)
# else:
#     exit(-1)
#
# if res_login.success:
#     token = res_login.body.token
#     print("[success] token:",token,res_login.elapsed)
#     print("[action] start request getstudentinfo:",stinfo.url)
#     if stinfo.type == "get":
#         res_stinfo = send_get('getinfo',stinfo.url,headers={"token":token})
#     elif stinfo.type == "post":
#         res_stinfo = send_post('getinfo', stinfo.url, headers={"token": token})
#     else:
#         exit(-1)
#     if res_stinfo.success:
#         print("[success] elapsed:",res_stinfo.elapsed)
#         pprint(res_stinfo.data)
#     else:
#         print("[failed] elapsed:", res_stinfo.elapsed)
#         print(res_stinfo.errorMsg)
# else:
#     print("[failed] elapsed:", res_login.elapsed)
#     print(res_login.errorMsg)