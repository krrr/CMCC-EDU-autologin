CMCC-EDU-autologin is a script for solving the captive portal of CMCC WLAN(only for SSID:CMCC-EDU).
It supports logging in,logging out,showing remaining time(optionally).
It works in a university located in Jinhua,Zhejiang Province,China.

这是一个用来登录CMCC WLAN（仅支持SSID为“CMCC-EDU”的接入点）的脚本。
它同时支持登录和登出，并有剩余时间提醒功能。
它在浙江省金华市某大学测试通过（其实也是在这里写的）。

Usage/使用方法
----
#####(Only python3 now)
Time Reminder enabled:
```
t.py username password remind
```
Time Reminder disabled:
```
t.py username password
```

#####(暂时只能工作在Python3下)
启用剩余时间提醒:
```
t.py username password remind
```
禁用剩余时间提醒:
```
t.py username password
```
Automation/自动化
----
Using the Scheduled task of Windows,you can login automatically when you connect to CMCC-EDU.see this [page](http://superuser.com/questions/262799/how-to-launch-a-command-on-network-connection-disconnection).
But logout can only be done manually.

借助Windows的计划任务功能，你能在成功连接至CMCC-EDU后自动登录。