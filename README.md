# tomcat_deploy
## 依赖tomcat 生成pid
```
vim bin/catalina.sh
变量初始后大概在setenv.sh后
CATALINA_PID=$CATALINA_BASE/tomcat.pid
```
## 2个tomcat 实例   8080端口  8180端口
## 启动iptable
## 使用
```bash
ssh -t root@192.168.0.1 <<EOF
python main.py start
if [[ \$? > 0 ]]; then
    echo "finish error"
    exit 1
fi
python main.py chg
if [[ \$? > 0 ]]; then
    echo "finish error"
    exit 1
fi
echo "finish success"
EOF
```
