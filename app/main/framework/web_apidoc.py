# -*- coding: utf-8 -*-
login = {
    "name":"login",
    "url":"http://121.43.101.211:8180/suime-user/student/login",
    "type":"post",
    "request":{"password":"md5_password","cellphone":"手机号"},
    "response":{}
}

mydocs = {
    "name":"mydocs",
    "url":"http://121.43.101.211:8380/suime-library/rest/stdoc/myAll",
    "type":"get",
    "request":"pageSize=10&sort=DESC&sortField=&token=stsmdbba7d15a94e4d9886408871ae233fb5&page=1&",
    "response":{"result":1,"body":{"pageSize":10,"data":[],"totalCount":0,"totalPageCount":0,"currentPageNo":1}}
}

logout = {
    "name": "logout",
    "url":"http://121.43.101.211:8180/suime-user/rest/student/logout",
    "type":"post",
    "request":{},
    "response":{}
}

getvalidatecode = {
    "name": "getvalidatecode",
    "url":"http://121.43.101.211:8180/suime-user/rest/verification/send",
    "type":"post",
    "request":{"reason":"reset_password","cellphone":"手机号"},
    "response":{}
}

resetpassword = {
    "name": "resetpassword",
    "url":"http://121.43.101.211:8180/suime-user/rest/student/resetPassword",
    "type":"post",
    "request":{"password":"md5_password","verificationCode":"6位数字","cellphone":"手机号"},
    "response":{}
}

getstudentinfo = {
    "name": "getstudentinfo",
    "url":"http://121.43.101.211:8180/suime-user/rest/student/info",
    "type":"get",
    "request":{},
    "response":{}
}

setstudentinfo = {
    "name": "setstinfo",
    "url":"http://121.43.101.211:8180/suime-user/rest/student/update",
    "type":"post",
    "request":{},
    "response":{}
}

printtask = {
    "name": "printtask",
    "url":"http://121.43.101.211:8880/suime-webapp/rest/student/printTask/listInCart",
    "type":"get",
    "request":{},
    "response":{}
}

library_banner = {
    "name": "library_banner",
    "url":"http://121.43.101.211:8380/suime-library/rest/index/banner",
    "type":"get",
    "request":{},
    "response":{}
}

library_hotcategory = {
    "name": "library_hotcategory",
    "url":"http://121.43.101.211:8380/suime-library/rest/tags/listIndex",
    "type":"get",
    "request":{},
    "response":{}
}

library_docs = {
    "name": "library_docs",
    "url":"http://121.43.101.211:8380/suime-library/rest/stdoc/index",
    "type":"get",
    "request":{},
    "response":{}
}

library_more = {
    "name": "library_more",
    "url":"http://121.43.101.211:8380/suime-library/rest/stdoc/list",
    "type":"get",
    "request":{},
    "response":{}
}

mycash = {
    "name": "mycash",
    "url":"http://121.43.101.211:8180/suime-user/rest/student/myCash",
    "type":"post",
    "request":{},
    "response":{}
}

order_all = {
    "name": "order_all",
    "url":"http://121.43.101.211:8880/suime-webapp/rest/printOrder/list",
    "type":"get",
    "request":{},
    "response":{}
}

order_unpaid = {
    "name": "order_unpaid",
    "url":"http://121.43.101.211:8880/suime-webapp/rest/printOrder/listUnpaid",
    "type":"get",
    "request":{},
    "response":{}
}

order_paid = {
    "name": "order_paid",
    "url":"http://121.43.101.211:8880/suime-webapp/rest/printOrder/listPaid",
    "type":"get",
    "request":{},
    "response":{}
}