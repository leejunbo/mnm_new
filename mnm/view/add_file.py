def add_domain_file(cls_path,cls_name,cls_ip,domain, ip, port=""):
    path = cls_path+"/"+cls_name+"/"+cls_ip
    f = open(path+"/" + domain +".conf", "w+", encoding='utf8')
    f.write(
        "\tserver{ \n"
        "\t\tlisten    80;\n"
        "\t\tserver_name  " + domain + ";\n"
		
        "\t\tlocation / {\n"
        "\t\tproxy_pass http://" + ip + port+";\n"
        "\t\tproxy_redirect off;\n"
        "\t\tproxy_set_header Host $host;\n"
        "\t\tproxy_set_header X-Real-IP $remote_addr;\n"
        "\t\tproxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        "\t\tproxy_connect_timeout 600;\n"
        "\t\tproxy_read_timeout 600;\n"
        "\t\t}\n"
        "\t}\n")
    f.close()
    h = open(cls_path+"/"+cls_name+"/hosts", "a+", encoding='utf8')
    h.write(ip + "   " + domain + "\n")
    h.close()

