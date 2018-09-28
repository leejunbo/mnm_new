def shell_rollback(cls_path):
    f = open(cls_path+"/"+"serverrollback.sh", "w+", encoding='utf8')
    f.write(
        "#!/bin/bash\n"
        "echo \"Nginx - Rollback!\"\n"

        "if [ -f /etc/nginx/nginx.conf ]\n"
        "then\n"
        "    rm -f /etc/nginx/nginx.conf\n"
        "    echo \"rm -f /etc/nginx/nginx.conf\"\n"
        "else\n"
        "    echo \"/etc/nginx/nginx.conf not exist!\"\n"
        "fi\n"
      
        "if [ -f /etc/nginx/nginx.conf.back ]\n"
        "then\n"
        "    mv /etc/nginx/nginx.conf.back /etc/nginx/nginx.conf\n"
        "    echo \"mv /etc/nginx/nginx.conf.back /etc/nginx/nginx.conf\"\n"
        "else\n"
        "    echo \"/etc/nginx/nginx.conf.back not exist!\"\n"
        "fi\n"
        
        "if [ -f /etc/hosts ]\n"
        "then\n"
        "    rm -f /etc/hosts\n"
        "    echo \"rm -f /etc/hosts\"\n"
        "else\n"
        "    echo \"'/etc/hosts' not exist!\"\n"
        "fi\n"

        "if [ -f /etc/hosts.back ]\n"
        "then\n"
        "    mv /etc/hosts.back /etc/hosts\n"
        "    echo \"mv /etc/hosts.back /etc/hosts\"\n"
        "else\n"
        "    echo \"/etc/hosts.back not exist!\"\n"
        "fi\n"

        "if [ -d $1/$2/ ]\n"
        "then\n"
        "    rm -rf $1/$2\n"
        "    echo \"rm -rf $1/$2/\"\n"
        "    nginx -s reload\n"
        "    echo \"nginx -s reload\"\n"
        "else\n"
        "    echo \"$1/$2/ not exist!\"\n"
        "fi\n")
    f.close()
