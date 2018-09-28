from flask import render_template, request, redirect, url_for, session, jsonify, abort, flash, json
import hashlib, re, os
from view.db import *
from view.common import *
from functools import wraps
import view.add_nginx_conf
import view.shell_file
import view.shell_rollback
import subprocess


def c_sql_data():
    data = get_cluster()
    return jsonify(data)


def c_add():
    if not session.get('logged_in'):
        flash('添加失败', 'error')
        flash('登陆信息已过期请重新登陆', 'alert')
        return jsonify("error")
    data = request.get_data()
    data = strtojson(data)
    cls_name = data['clsName']
    cls_path = data['clsPath']
    cls_ip = data['clsIp']
    path = cls_path+"/"+cls_name+"/"+cls_ip
    path1 = cls_path+"/"+cls_name
    r = [cls_name, cls_path, cls_ip]
    pattern = re.compile(
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.'
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)')
    p = pattern.search(r[2])
    if p is None:
        flash(r[2] + '的IP格式不匹配')
        return jsonify(data)
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT cls_name,cls_ip FROM clustermanage")
        cur = cursor.fetchall()
        for i in range(len(cur)):
            if cur[i][1] == r[2]:
                flash(r[2] + ' IP已存在', 'alert')
                return jsonify("error")
            if cur[i][0] == r[0]:
                flash(r[0] + '已存在', 'alert')
                return jsonify("error")
                
        subprocess.check_call(["mkdir", "-p", path])
        view.shell_file.shell_file(cls_path)
        view.add_nginx_conf.add_nginx_conf(path1,cls_ip)
        subprocess.check_call(["ssh",cls_ip,"sh",cls_path+"/serverset.sh",cls_path,cls_name])
        cursor.execute("INSERT INTO clustermanage (cls_name,cls_path,cls_ip) VALUES (%s,%s,%s)", (r[0], r[1], r[2]))
        db.commit()
    except ImportError:
        db.rollback()
    subprocess.check_call(["ssh",cls_ip,"nginx", "-s", "reload"])
    flash(cls_name + '的信息添加成功', 'success')
    return jsonify("cluster")


def c_edit():
    if not session.get('logged_in'):
        flash('修改失败', 'error')
        flash('登陆信息已过期请重新登陆', 'alert')
        return jsonify("error")
    data = request.get_data()
    data = strtojson(data)
    cls_id = data["clsId"]
    cls_name = data["clsName"]
    cls_path = data["clsPath"]
    cls_ip = data["clsIp"]
    r = [cls_name, cls_path, cls_ip]
    pattern = re.compile(
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.'
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)')
    p = pattern.search(r[2])
    if p is None:
        flash(r[2] + '的IP格式不匹配')
        return jsonify("error")
    db = get_db()
    try:
        cursor = db.cursor()
        sql = "select cls_name,cls_path,cls_ip from clustermanage where cls_id=" + cls_id
        cursor.execute(sql)
        cur = cursor.fetchone()
        cls_name_old = cur[0]
        cls_path_old = cur[1]
        cls_ip_old = cur[2]
        i = (cls_name == cls_name_old) and (cls_path == cls_path_old) and (cls_ip == cls_ip_old)
        if i:
            flash(cls_name+' 信息未改动', 'alert')
            return jsonify('alert')
      #  sql = "SELECT cls_path FROM clustermanage WHERE cls_id=" + cls_id
      #  cursor.execute(sql)
      #  cur = cursor.fetchone()
      #  cls_path_old = cur[0]
      #  with open('/etc/nginx/nginx.conf', 'r') as f:
      #      f = f.read()
      #      f = f.replace(cls_path_old, cls_path)
      #  with open('/etc/nginx/nginx.conf', 'w+') as file:
      #      file.write(f)
        sql = "UPDATE clustermanage SET cls_name='" + cls_name + "', cls_path='" + cls_path + "',cls_ip='" + \
              cls_ip + "' WHERE cls_id=" + cls_id
        cursor.execute(sql)
        db.commit()
        subprocess.check_call(["ssh",cls_ip,"nginx", "-s", "reload"])
    except ImportError:
        db.rollback()
    flash(cls_name + '的信息修改成功', 'success')
    return jsonify("success")

def c_delete():
    if not session.get("logged_in"):
        flash('修改失败', 'error')
        flash('登陆信息已过期请重新登陆', 'alert')
        return jsonify("error")
    data = request.get_data()
    data = strtojson(data)
    cls_id = data["clsId"]
    cls_name = data["clsName"]
    cls_path = data["clsPath"]
    cls_ip = data["clsIp"]
    path=cls_path+"/"+cls_name+"/"+cls_ip
    for root, dirs, files in os.walk(path):
        print(os.walk(path))
        print(root)
        print(dirs)
        print(files)
        for file in files:
            if os.path.splitext(file)[1] == '.conf':
                flash("路径"+path+"的目录下存在.conf配置文件", "alert")
            return jsonify("alert")
    db = get_db()
    try:
        cursor = db.cursor()
        sql = "DELETE FROM clustermanage WHERE cls_id=" + cls_id
        cursor.execute(sql)
        view.shell_rollback.shell_rollback(cls_path)
        subprocess.check_call(["ssh",cls_ip,"sh",cls_path+"/serverrollback.sh",cls_path,cls_name])
        db.commit()
    except ImportError:
        db.rollback()
        flash(cls_name + '的信息删除失败', 'error')
        return jsonify("error")
    flash(cls_name + '的信息删除成功', 'success')
    return jsonify("success")
