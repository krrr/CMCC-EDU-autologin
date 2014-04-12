CMCC-EDU-autologin is a script for solving the captive portal of CMCC WLAN(only for SSID:CMCC-EDU).
It only supports logging in.
It works in Zhejiang Province,China.

这是一个用来登录CMCC公共热点（仅支持SSID为“CMCC-EDU”的接入点）的脚本。
它只支持登录（没有保持登录状态、登出的功能）。
它在浙江省金华市测试通过。

**(Requires Python3 with Requests library)/(需要Python3与Requests库)**
Usage/使用方法
----
Edit config.ini first.Then run t.py .
Use pythonw.exe to run t.py if GUI(Windows only) enabled.

先编辑config.ini文件，然后运行t.py。如果启用了GUI（Windows限定），用pythonw来运行t.py。


----
Using the Scheduled Task of Windows,it can run automatically when connected to CMCC-EDU:[HOWTO](http://superuser.com/questions/262799/how-to-launch-a-command-on-network-connection-disconnection).


借助Windows的计划任务功能，可以在成功连接至CMCC-EDU后自动运行来登录。