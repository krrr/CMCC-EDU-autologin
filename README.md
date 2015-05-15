CMCC-EDU-autologin is a script for solving the captive portal of CMCC WLAN (only for SSID:CMCC-EDU).
It only supports logging in.
It works in Zhejiang Province, China.

Requires: Python3, requests, pynotify2 (if GUI notify for Unix enabled)

这是一个用来登录CMCC公共热点（仅支持SSID为“CMCC-EDU”的接入点）的脚本。
只支持登录（没有保持登录状态、登出的功能），仅在浙江省金华市测试通过。

依赖：Python3，Requests，pynotify (如果需要使用Unix下的GUI)

Usage/使用方法
----
Edit `config.ini` first. Then run `t.py`.
Use `pythonw.exe` to run `t.py` or rename it to `t.pyw` if GUI type is Win.

先编辑`config.ini`文件，然后运行`t.py`。如果启用了Win的GUI，用pythonw来运行`t.py`或者把它重命名为`t.pyw`


----
Using the Scheduled Task of Windows,it can run automatically when connected to CMCC-EDU: [HOWTO](http://superuser.com/questions/262799/how-to-launch-a-command-on-network-connection-disconnection)


借助Windows的计划任务功能，可以在成功连接至CMCC-EDU后自动运行来登录。
