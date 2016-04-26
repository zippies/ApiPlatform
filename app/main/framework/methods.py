import random
import hashlib
import pickle
import os

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
