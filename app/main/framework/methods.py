import random
import hashlib
import pickle
import os
import pymysql.cursors
from config import Config

class EnvObj(object):
    def __repr__(self):
        return "<EnvironmentObject>"

def toMD5(str):
    hash = hashlib.md5()
    hash.update(str.encode())
    return hash.hexdigest()

def randomInt(length=8):
    a = eval("1" + "0"*(length-1))
    b = eval("1" + "0"*length) - 1
    return random.randint(a,b)

def randomPhoneNum():
    phonepres = [134,135,136,137,138,139,150,151,152,157,158,159,182,183,184,187,188,178,147,130,131,132,155,156,185,186,176,145,133,153,180,181,189 ,177]
    pre = random.sample(phonepres,1)[0]
    after = randomInt(8)
    return "%s%s" %(pre,after)

def setenv(key,value,user):
    env = None
    if os.path.exists("data/%s_%s.pkl" %(user.id,user.nickname)):
        env = pickle.load(open("data/%s_%s.pkl" %(user.id,user.nickname), 'rb'))
    else:
        env = EnvObj()

    setattr(env,key,value)
    pickle.dump(env,open("data/%s_%s.pkl" %(user.id,user.nickname),"wb"))
    return True

def getenv(key,user):
    env = None
    if os.path.exists("data/%s_%s.pkl" %(user.id,user.nickname)):
        env = pickle.load(open("data/%s_%s.pkl" %(user.id,user.nickname),'rb'))
        if hasattr(env,key):
            return getattr(env,key)
        else:
            return None
    else:
        return None

def delenv(key,user):
    env = None
    if os.path.exists("data/%s_%s.pkl" %(user.id,user.nickname)):
        env = pickle.load(open("data/%s_%s.pkl" %(user.id,user.nickname),'rb'))
        if hasattr(env,key):
            delattr(env,key)
            pickle.dump(env, open("data/%s_%s.pkl" % (user.id, user.nickname), "wb"))
            return True
        else:
            return None
    else:
        return None

def execSQL(sql,host=None,user=None,password=None,db=None,port=3306):
    if not host or not user or not password or not db or not port:
        host = Config.db_host
        user = Config.db_user
        password = Config.db_password
        db = Config.db_database
        port = Config.db_port or 3306

    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        db=db,
        port=port,
        charset='utf8'
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            if sql.strip().lower().startswith("select"):
                result = cursor.fetchall()
                return result
            else:
                return True
    finally:
        try:
            connection.close()
        except Exception as e:
            print("close db failed:",e)

if __name__ == "__main__":
    sql = "select id,student_id,printshop_id,state from wenji_print_order limit 10"
    execSQL(sql)