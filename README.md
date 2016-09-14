用来登录CMCC公共热点（仅支持SSID为“CMCC-EDU”的接入点）的脚本。
只支持登录（没有保持登录状态、登出的功能），仅在浙江省金华市测试通过。

依赖：Python3，Requests，notify2 (如果需要使用Unix的GUI)

使用方法
----
先编辑`config.ini`文件，然后运行`main.py`。如果启用了Windows的GUI则需要用pythonw来运行`main.py`或者把它重命名为`main.pyw`

借助Windows的计划任务功能，可以在成功连接至CMCC-EDU后自动运行来登录。
[HOWTO](http://superuser.com/questions/262799/how-to-launch-a-command-on-network-connection-disconnection)
