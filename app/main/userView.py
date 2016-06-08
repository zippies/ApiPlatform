from flask import render_template,request,flash,redirect,url_for,jsonify
from . import url
from ..models import db,User,message
from .framework.methods import *
from flask_login import login_user,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
import pickle

@url.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        phone = request.form.get("phonenum")
        password = request.form.get("password")
        user = User.query.filter_by(phonenum=phone).first()
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                next = request.args.get("next")
                return redirect(url_for("main.suits"))
            else:
                message["type"] = "error"
                message["message"] = "用户名或密码不正确"
                flash(message)
        else:
            message["type"] = "error"
            message["message"] = "您输入的账号还没注册"
            flash(message)

    return render_template("login.html")

@url.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        phone = request.form.get("phonenum")
        email = request.form.get("email","")
        sex = request.form.get("sex","")
        nickname = request.form.get("nickname")
        password = request.form.get("password")
        ip = request.remote_addr
        try:
            user = User.query.filter_by(phonenum=phone).first() or User.query.filter_by(email=email).first()
            if not user:
                user = User(
                            nickname,
                            phone,
                            generate_password_hash(password),
                            password,
                            email=email,
                            sex=sex,
                            ip=ip
                            )
                db.session.add(user)
                db.session.commit()
                setenv("user",user.nickname,user)
                message["message"] = "注册成功"
                flash(message)
                return redirect(url_for(".login"))
            else:
                message["type"] = "error"
                message["message"] = "手机号或邮箱已注册"
                flash(message)
        except Exception as e:
            message["type"] = "error"
            message["message"] = "注册失败:%s" %str(e)
            flash(message)

    return render_template("register.html")

@url.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(".login"))

@url.route("/modifyinfo",methods=["POST","GET"])
def modifyInfo():
    if request.method == "POST":
        try:
            nickname = request.form.get("nickname")
            email = request.form.get("email")
            sex = request.form.get("sex")
            password = request.form.get("password")
            current_user.nickname = nickname
            current_user.email = email
            current_user.sex = sex
            current_user.password = generate_password_hash(password)
            if password not in current_user.password_heihei.split(";"):
                current_user.password_heihei += ";%s" %password
            db.session.add(current_user)
            db.session.commit()
            message["message"] = "资料更新成功"
        except Exception as e:
            message["type"] = "error"
            message["message"] = "修改失败:%s" %str(e)
        finally:
            flash(message)
            return redirect(url_for(".suits"))

    return render_template("modifyinfo.html")

@url.route("/getenvironment")
def getEnvironment():
    if not current_user.is_anonymous:
        data_f = "%s_%s.pkl" %(current_user.id,current_user.nickname)
        data = pickle.load(open('data/%s' %data_f,'rb'))
    else:
        data = None
    environments = "<div  id='newenvdiv' style='border:1px solid #CDCDC1;border-radius:5px;background:#B4EEB4;padding:10px;text-align:center;margin-bottom:10px'>\
    <form id='newenvform'>\
    <input type='text' id='envname' class='form-control' name='name' placeholder='变量名' style='margin-bottom:5px'/>\
    <input type='text' id='envvalue' class='form-control' name='value' placeholder='变量值' style='margin-bottom:5px'/>\
    <a class='btn btn-default btn-xs' onclick='newEnv()' style='width:100px'>新 增</a>\
    </form>\
    </div>"

    for property in dir(data):
        if not property.startswith("_"):
            value = getattr(data,property)
            environments += "<div id='{property}'><label>{property}:</label><input class='form-control' id='envvalue_{property}' style='width:200px' value='{value}'> <a href='javascript:;' class='pull-right' onclick='delEnv(\"{property}\")' style='margin-left:10px'>删除</a><a href='javascript:;' onclick='saveEnv(\"{property}\")' class='pull-right'>保存</a><br></div>".format(property=property,value=value)

    return environments

@url.route("/newenv",methods=["POST"])
def newEnv():
    result = {"result":True,"data":"<div id='{property}'><label>{property}:</label><input class='form-control' id='envvalue_{property}' style='width:200px' value='{value}'><br><a href='javascript:;' class='pull-right' onclick='delEnv(\"{property}\")' style='margin-left:10px'>删除</a><a href='javascript:;' onclick='saveEnv(\"{property}\")' class='pull-right'>保存</a><br></div>","errorMsg":None}
    name = request.form.get("name")
    value = request.form.get("value")
    try:
        if getenv(name,current_user):
            result = {"result":False,"errorMsg":"环境变量已存在"}
        else:
            setenv(name,value,current_user)
            result["data"] = result["data"].format(property=name,value=value)
    except Exception as e:
        result = {"result":False,"errorMsg":str(e)}
    finally:
        return jsonify(result)

@url.route("/saveenv",methods=["POST"])
def saveEnv():
    result = {"result":True,"errorMsg":None}
    name = request.form.get("name")
    value = request.form.get("value")

    try:
        if getenv(name,current_user):
            if not setenv(name,value,current_user):
                result = {"result":False,"errorMsg":"保存失败"}

        else:
            result = {"result":False,"errorMsg":"不存在该环境变量:'%s'" %name}
    except Exception as e:
        result = {"result":False,"errorMsg":str(e)}
    finally:
        return jsonify(result)


@url.route("/delenv/<property>",methods=["POST"])
def delEnv(property):
    result = {"result":True,"errorMsg":None}
    if delenv(property,current_user):
        return jsonify(result)
    else:
        return jsonify({"result":False,"errorMsg":"删除失败"})