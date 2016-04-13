# -*- coding: utf-8 -*-
android_mydocs = {
    "name":"mydocs",
    "url":"http://121.43.101.211:8380/suime-library/m2/stdoc/myAll",
    "type":"get",
    "request":"pageSize=10&sort=DESC&sortField=&token=stsmdbba7d15a94e4d9886408871ae233fb5&page=1&",
    "response":{"result":1,"body":{"pageSize":10,"data":[],"totalCount":0,"totalPageCount":0,"currentPageNo":1}}
}

android_logout = {
    "name": "logout",
    "url":"http://121.43.101.211:8180/suime-user/m2/student/logout",
    "type":"post",
    "request":{},
    "response":{}
}

android_getvalidatecode = {
    "name": "getvalidatecode",
    "url":"http://121.43.101.211:8180/suime-user/m2/verification/send",
    "type":"post",
    "request":{"reason":"reset_password","cellphone":"手机号"},
    "response":{}
}

android_resetpassword = {
    "name": "resetpassword",
    "url":"http://121.43.101.211:8180/suime-user/m2/student/resetPassword",
    "type":"post",
    "request":{"password":"md5_password","verificationCode":"6位数字","cellphone":"手机号"},
    "response":{}
}

android_getstudentinfo = {
    "name": "getstudentinfo",
    "url":"http://121.43.101.211:8180/suime-user/m2/student/info",
    "type":"get",
    "request":{},
    "response":{}
}

android_setstudentinfo = {
    "name": "setstinfo",
    "url":"http://121.43.101.211:8180/suime-user/m2/student/update",
    "type":"post",
    "request":{},
    "response":{}
}

android_printtask = {
    "name": "printtask",
    "url":"http://121.43.101.211:8880/suime-webapp/m2/student/printTask/listInCart",
    "type":"get",
    "request":{},
    "response":{}
}

android_library_banner = {
    "name": "library_banner",
    "url":"http://121.43.101.211:8380/suime-library/m2/index/banner",
    "type":"get",
    "request":{},
    "response":{}
}

android_library_hotcategory = {
    "name": "library_hotcategory",
    "url":"http://121.43.101.211:8380/suime-library/m2/tags/listIndex",
    "type":"get",
    "request":{},
    "response":{}
}

android_library_docs = {
    "name": "library_docs",
    "url":"http://121.43.101.211:8380/suime-library/m2/stdoc/index",
    "type":"get",
    "request":{},
    "response":{}
}

android_library_more = {
    "name": "library_more",
    "url":"http://121.43.101.211:8380/suime-library/m2/stdoc/list",
    "type":"get",
    "request":{},
    "response":{}
}

android_mycash = {
    "name": "mycash",
    "url":"http://121.43.101.211:8180/suime-user/m2/student/myCash",
    "type":"post",
    "request":{},
    "response":{}
}

android_order_all = {
    "name": "order_all",
    "url":"http://121.43.101.211:8880/suime-webapp/m2/printOrder/list",
    "type":"get",
    "request":{},
    "response":{}
}

android_order_unpaid = {
    "name": "order_unpaid",
    "url":"http://121.43.101.211:8880/suime-webapp/m2/printOrder/listUnpaid",
    "type":"get",
    "request":{},
    "response":{}
}

android_order_paid = {
    "name": "order_paid",
    "url":"http://121.43.101.211:8880/suime-webapp/m2/printOrder/listPaid",
    "type":"get",
    "request":{},
    "response":{}
}