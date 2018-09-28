from flask import render_template, request, redirect, url_for, session, jsonify, abort, flash, json
import hashlib, re, os
from view.db import *
from functools import wraps
import view.del_line
import view.add_file
import subprocess

def required(f):
    @wraps(f)
    def check(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return check


def d_sql_data():
    data = get_device()
    return jsonify(data)

	
def config_file_info():
    data = request.get_data()
    data = strtojson(data)
    f_domain = data['domain']
    cls_name = data['cls_name']
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("select cls_name,cls_path,cls_ip from clustermanage where cls_name="+"'"+cls_name+"'")
        cur = cursor.fetchone()
        cls_name = cur[0]
        cls_path = cur[1]
        cls_ip = cur[2]
        with open(cls_path+'/'+cls_name+'/'+cls_ip+'/'+f_domain+'.conf', 'r') as f:
            f = f.read()
        db.commit()
    except ImportError:
        db.rollback()
        flash('读取配置文件信息失败','error')
        return jsonify('error')
    return jsonify(f)


def config_f():
    return render_template('edit_text.html')


def config_newfile():
    data = request.get_data()
    data = strtojson(data)
    nf_domain = data['domain']
    confFile = data['nfInfo']
    cls_name = data['cls_name']
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("select cls_name,cls_path,cls_ip from clustermanage where cls_name="+"'"+cls_name+"'")
        cur = cursor.fetchone()
        cls_name = cur[0]
        cls_path = cur[1]
        cls_ip = cur[2]
        with open(cls_path+'/'+cls_name+'/'+cls_ip+'/'+nf_domain+'.conf', 'r') as file:
            file = file.read()
            if file == confFile:
                flash('域名为 '+nf_domain+' 的配置文件信息未修改','alert')
                return jsonify("alert")
        with open(cls_path+'/'+cls_name+'/'+cls_ip+'/'+nf_domain+'.conf','w+') as f:
            f = f.write(confFile)
        db.commit()
    except ImportError:
        db.rollback()
        flash('域名为 '+nf_domain+' 的配置文件信息修改失败','error')
        return jsonify("error")
    flash('域名为 '+nf_domain+' 的配置文件信息修改成功','success')
    subprocess.check_call(["ssh",cls_ip,"nginx", "-s","reload"])
    return jsonify(f)
	

def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))


def login():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        """cursor.execute("SELECT account, psw FROM register ")"""
        cursor.execute("SELECT username, password FROM user ")
        cur = cursor.fetchall()
        for c in cur:
            sqlstr = "".join(c)
            poststr = request.form['username'] + request.form['password']
            if sqlstr != poststr:
                session.setdefault("login_error", "用户名或密码错误")
            else:
                session.setdefault("logged_in", True)
                session.pop("login_error", None)
                return redirect(url_for("index"))
    return render_template('domain/login.html')


def show_entries():
    return render_template('domain/domain.html', datas=datas())


def datas():
    db = get_db()
    cursor = db.cursor()
    sql = "SELECT id,domain,ip FROM domainmanage "
    cursor.execute(sql)
    cur = cursor.fetchall()
    entries = [dict(id=row[0], domain=row[1], ip=row[2]) for row in cur]
    _datas = {
        'show_entries': entries,
    }
    db.commit()
    return _datas


def nodesName():
    db = get_db()
    cursor = db.cursor()
    sql = "select cls_name from clustermanage"
    cursor.execute(sql)
    cur = cursor.fetchall()
    nodes1 = [dict(node=row[0]) for row in cur]    
    nodes = {
        'nodes': nodes1
    }
    db.commit()
    return nodes

def register():
    if request.method == 'POST':
        r = [request.form['username'], request.form['password']]
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO user (username, password) VALUES (%s,%s)", (r[0], r[1]))
            db.commit()
            flash('注册成功', 'success')
        except ImportError:
            db.rollback()
            flash('注册失败', 'err')
            return render_template("domain/register.html")
    return render_template("domain/register.html")


def save():
    if not session.get('logged_in'):
        flash('修改失败', 'error')
        flash('登陆信息已过期请重新登陆', 'alert')
        return jsonify("error")
    data = request.get_data()
    data = strtojson(data)
    d_id = data["id"]
    cls_name = data["cls_name"]
    domain = data["domain"]
    ip = data["ip"]
    port = data["port"]
    if port=="":
        port = "80"
    db = get_db()
    cursor = db.cursor()
    pattern = re.compile(
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.'
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)')
    p = pattern.search(ip)
    if p is None:
        flash('IP格式不匹配', 'alert')
        return redirect(url_for('edit'))
    sql = "SELECT domain,ip,port FROM domainmanage WHERE id=" + d_id
    cursor.execute(sql)
    cur = cursor.fetchone()
    domain_old = cur[0]
    ip_old = cur[1]
    port_old = cur[2]
    sql_search = "SELECT domain,ip,port,id FROM domainmanage"
    cursor.execute(sql_search)
    cur_search = cursor.fetchall()
    for i in range(len(cur_search)):
        j = (cur_search[i][0] == domain) and (cur_search[i][1] == ip) and (cur_search[i][2] == port) and (str(cur_search[i][3]) == d_id)
        k = (cur_search[i][0] == domain) and (str(cur_search[i][3]) != d_id)
       # print(cur_search[i][0] == domain)
       # print(cur_search[i][3] != str(d_id))
       # print(isinstance(d_id,str))
       # print(isinstance(str(cur_search[i][3]),str))
        if j:
            flash(domain+' 信息未作改动', 'alert')
            return jsonify('ok')
        if k:
            flash(domain_old + "不能修改为 " + domain + ','+domain+' 域名已存在', 'alert')
            return jsonify('ok') 
    try:
        sql = "UPDATE domainmanage SET domain='" + domain + "',ip='" + ip + "',port='"+ port +"' WHERE id=" + d_id
        cursor.execute(sql)
        db.commit()
    except ImportError:
        db.rollback()
        flash(domain_old+' 信息修改失败','error')
    view.del_line.del_line(ip_old)  # 删除旧的ip
    cursor.execute("select cls_name,cls_path,cls_ip from clustermanage where cls_name="+"'"+cls_name+"'")
    cur = cursor.fetchone()
    cls_name = cur[0]
    cls_path = cur[1]
    cls_ip = cur[2]
    path = cls_path+'/'+cls_name+'/'+cls_ip
    if  port=="80":
        with open(path+'/'+domain_old+'.conf', 'r') as f:
            f = f.read()
            f = f.replace(domain_old,domain)
            f = f.replace(port_old,port)
            f.replace(ip_old,ip)
        with open(path+'/'+domain+'.conf','w+') as file:
            file = file.write(f)
    else:
        with open(path+'/'+domain_old+'.conf', 'r') as f:
            f = f.read()
            f = f.replace(domain_old,domain)
            f = f.replace(ip_old,ip)
            f = f.replace(port_old,port)
            if port_old=="80":
               f = f.replace(port,"80",1)
            with open(path+'/'+domain+'.conf','w+') as file:
               file.write(f)
    flash('域名为 '+ domain +' 的信息修改成功', 'success')
    subprocess.check_call(["ssh",cls_ip,"nginx", "-s","reload"])
    return jsonify("ok")


def add():
    if not session.get('logged_in'):
        flash('添加失败', 'error')
        flash('登陆信息已过期请重新登陆', 'alert')
        return jsonify("error")
    data = request.get_data()
    data = strtojson(data)
    domain=data['domain']
    ip=data['ip']
    port=data['port']
    cls_name=data['cls_name']
    print("====="+cls_name+"=====")
    r = [domain, ip, port]
    pattern = re.compile(
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.'
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)')
    p = pattern.search(r[1])
    if p is None:
        flash('IP格式不匹配', 'alert')
        return jsonify(data)
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("select domain from domainmanage")
        cur = cursor.fetchall()
        for i in range(len(cur)):
            if cur[i][0] == r[0]:
                flash(r[0]+' 域名已存在', 'alert')
                return jsonify(data)
        cursor.execute("select cls_ip,cls_path from clustermanage where cls_name="+"'"+cls_name+"'")
        cur = cursor.fetchone()
        cls_ip=cur[0]
        cls_path=cur[1]
        cursor.execute("INSERT INTO domainmanage (domain,ip,port,cls_name) VALUES (%s,%s,%s,%s)", (r[0], r[1], r[2],cls_name))
        if r[2]=="":
            view.add_file.add_domain_file(cls_path,cls_name,cls_ip, r[0], r[1], ":80")
        else:
            p=":"+r[2]
            view.add_file.add_domain_file(cls_path,cls_name,cls_ip, r[0], r[1], p)
        db.commit()
    except ImportError:
        db.rollback()
        flash(r[0]+' 添加失败','error')
        return jsonify("error")
    flash(r[0]+' 添加成功','success')
    subprocess.check_call(["ssh",cls_ip,"nginx", "-s","reload"])
    return jsonify("ok")


def delete():
    if not session.get('logged_in'):
        flash('删除失败', 'error')
        flash('登陆信息已过期请重新登陆', 'alert')
        return jsonify("error")
    data = request.get_data()
    data = strtojson(data)
    del_id = data['del_id']
    cls_name = data['cls_name']
    db = get_db()
    try:
        cursor = db.cursor()
        d_sql = "SELECT domain,ip FROM domainmanage WHERE id=" + del_id
        cursor.execute(d_sql)
        cur1 = cursor.fetchone()
        domain = cur1[0]
        ip = cur1[1]
        ipdomain = ip + "   " + domain
        c_sql = "select cls_name,cls_path,cls_ip from clustermanage where cls_name=" + "'"+cls_name+"'"
        cursor.execute(c_sql)
        cur2 = cursor.fetchone()
        cls_name = cur2[0]
        cls_path = cur2[1]
        cls_ip = cur2[2]
        path = cls_path+"/"+cls_name+"/"+cls_ip
        sql = "DELETE FROM domainmanage WHERE id=" + del_id
        cursor.execute(sql)
        db.commit()
    except ImportError:
        db.rollback()
        flash(domain+' 删除失败','error')
    del_file(path,domain)
    view.del_line.del_line(ipdomain)
    flash(domain+' 删除成功', 'success')
    subprocess.check_call(["ssh",cls_ip,"nginx", "-s","reload"])
    return jsonify("ok")


def strtojson(jsonstr):
    jsondict = json.loads(jsonstr, encoding="utf-8")
    return jsondict


def del_file(path,cur):
    file = path+"/" + cur + ".conf"
    os.remove(file)



