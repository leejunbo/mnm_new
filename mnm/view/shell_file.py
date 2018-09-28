def shell_file(cls_path):
    f = open(cls_path+"/"+"serverset.sh", "w+", encoding='utf8')
    f.write(
        "#!/bin/bash\n"
        "echo \"Nginx - Client deployment!\"\n"
        
        "if [ -f /etc/nginx/nginx.conf.back ]\n"
        "then\n"
        "    rm -f /etc/nginx/nginx.conf.back\n"
        "    rm -f /etc/nginx/nginx.conf\n"
        "    echo \"rm -f /etc/nginx/nginx.conf.back\"\n"
        "elif [ -f /etc/nginx/nginx.conf ]\n"
        "then\n"
        "    mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.back\n"
        "else\n"
        "    echo \"/etc/nginx/nginx.conf not exist. only support nginx installed by yum\"\n"
        "    break\n"
        "fi\n"
      
        "if [ -f $1/$2/nginx.conf ]\n"
        "then\n"
        "    ln -s $1/$2/nginx.conf /etc/nginx/\n"
        "    echo \"ln -s $1/$2/nginx.conf /etc/nginx/\"\n"
        "else\n"
        "    echo \"'$1/$2/nginx.conf' not exist\"\n"
        "fi\n"

        "if [ -f /etc/hosts ]\n"
        "then\n"
        "    mv /etc/hosts /etc/hosts.back\n"
        "    echo \"mv /etc/hosts /etc/hosts.back\"\n"
        "else\n"
        "    echo \" '/etc/hosts' not exist\"\n"
        "fi\n"

        "if [ ! -f $1/$2/hosts ]\n"
        "then\n"
        "    touch $1/$2/hosts\n"
        "    ln -s $1/$2/hosts /etc/hosts\n"
        "    cat /etc/hosts.back > /etc/hosts\n"
        "    nginx -s reload\n"
        "else\n"
        "    echo \"$1/$2/hosts exist\"\n"
        "fi\n")
    f.close()

