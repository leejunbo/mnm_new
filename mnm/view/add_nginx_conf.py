def add_nginx_conf(path,cls_ip):
    f = open(path+"/nginx.conf","w+",encoding="utf8")
    f.write(
        "#user  nobody;\n"
        "worker_processes  1;\n"

        "#error_log  logs/error.log;\n"
        "#error_log  logs/error.log  notice;\n"
        "#error_log  logs/error.log  info;\n"

        "#pid        logs/nginx.pid;\n"


        "events {\n"
        "    worker_connections  1024;\n"
        "}\n"


        "http {\n"
        "    include       mime.types;\n"
        "    default_type  application/octet-stream;\n"

        "    #log_format  main  '$remote_addr - $remote_user [$time_local] \"$request\" '\n"
        "    #                  '$status $body_bytes_sent \"$http_referer\" '\n"
        "    #                  '\"$http_user_agent\" \"$http_x_forwarded_for\" ';\n"

        "    #access_log  logs/access.log  main;\n"

        "    sendfile        on;\n"
        "    #tcp_nopush     on;\n"

        "    #keepalive_timeout  0;\n"
        "    keepalive_timeout  65;\n"

        "    #gzip  on;\n"
        
        "    include /etc/nginx/conf.d/*.conf;\n"
        "    include "+path+"/"+cls_ip+"/*.conf;\n"

        "    server {\n"
        "        listen       80;\n"
        "        server_name  localhost;\n"

        "        #charset koi8-r;\n"

        "        #access_log  logs/host.access.log  main;\n"

        "       location / {\n"
        "            root   html;\n"
        "            index  index.html index.htm;\n"
        "        }\n"

        "        #error_page  404              /404.html;\n"

        "        # redirect server error pages to the static page /50x.html\n"
        "        #\n"
        "        error_page   500 502 503 504  /50x.html;\n"
        "        location = /50x.html {\n"
        "            root   html;\n"
        "        }\n"

        "        # proxy the PHP scripts to Apache listening on 127.0.0.1:80\n"
        "        #\n"
        "        #location ~ \.php$ {\n"
        "        #    proxy_pass   http://127.0.0.1;\n"
        "        #}\n"

        "        # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000\n"
        "        #\n"
        "        #location ~ \.php$ {\n"
        "        #    root           html;\n"
        "        #    fastcgi_pass   127.0.0.1:9000;\n"
        "        #    fastcgi_index  index.php;\n"
        "        #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;\n"
        "        #    include        fastcgi_params;\n"
        "        #}\n"

        "        # deny access to .htaccess files, if Apache's document root\n"
        "        # concurs with nginx's one\n"
        "        #\n"
        "        #location ~ /\.ht {\n"
        "        #    deny  all;\n"
        "        #}\n"
        "    }\n"

        "    # another virtual host using mix of IP-, name-, and port-based configuration\n"
        "    #\n"
        "    #server {\n"
        "    #    listen       8000;\n"
        "    #    listen       somename:8080;\n"
        "    #    server_name  somename  alias  another.alias;\n"

        "    #    location / {\n"
        "    #        root   html;\n"
        "    #        index  index.html index.htm;\n"
        "    #    }\n"
        "    #}\n"


        "    # HTTPS server\n"
        "    #\n"
        "    #server {\n"
        "    #    listen       443 ssl;\n"
        "    #    server_name  localhost;\n"

        "    #    ssl_certificate      cert.pem;\n"
        "    #    ssl_certificate_key  cert.key;\n"

        "    #    ssl_session_cache    shared:SSL:1m;\n"
        "    #    ssl_session_timeout  5m;\n"

        "    #    ssl_ciphers  HIGH:!aNULL:!MD5;\n"
        "    #    ssl_prefer_server_ciphers  on;\n"

        "    #    location / {\n"
        "    #        root   html;\n"
        "    #        index  index.html index.htm;\n"
        "    #    }\n"
        "    #}\n"
        "}\n")
    f.close()
