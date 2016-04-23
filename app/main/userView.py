from flask import render_template,request,flash,redirect,url_for
from werkzeug.exceptions import abort
from . import url
from ..models import db,User,message
from flask.ext.login import login_user,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash


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
            user = User.query.filter_by(phonenum=phone).first()
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
                message["message"] = "注册成功"
                flash(message)
                return redirect(url_for(".login"))
            else:
                message["type"] = "error"
                message["message"] = "手机号已注册"
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
def modifyinfo():
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