import re
import urllib.request as urlreq
import http.cookiejar
import sys
import balloon

username = ''
passwd = ''

cj = http.cookiejar.LWPCookieJar('cookie.txt')
opener = urlreq.build_opener(urlreq.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0;\
Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.3072\
9; .NET CLR 3.0.30729; Tablet PC 2.0)')]

temp = str(opener.open('http://8.8.8.8').read())
# iURL: for getting lURL,validates,userip,acip...
# lURL: for sending all data to login(HTTP POST).
iURL = re.search(r'<iframe class="Wp_frame" id="Wp_frame" src="(.+?)" ', temp).group(1)
serverip = re.search(r'https://(.+?):', iURL).group(1)
lURL = 'https://' + serverip + ':7090/zmcc/cmcc_edu_do_login.php'

userip = re.search(r'wlanuserip=(.+?)&', iURL).group(1)
acname = re.search(r'wlanacname=(.+?)&', iURL).group(1)
acip = re.search(r'wlanacip=(.+?)&', iURL).group(1)

temp = str(opener.open(iURL).read())
print(temp.find('本月套餐已'))
try:  # get validation code
    hidvad = re.search(r"validateid\\'  value=\\'(.+?)\\'", temp).group(1)
    hidvad = hidvad.replace('|', '%7C')
    vad = hidvad[:4]
    data = 'username=%s&password=%s&loginvalidate=%s&loginhiddenvalidate=%s\
&loginmode=static&wlanacssid=CMCC-EDU&wlanacname=%s&wlanacip=%s\
&wlanuserip=%s&issaveinfo=1'\
    % (username, passwd, vad, hidvad, acname, acip, userip)
except:  # no validation code
    data = 'username=%s&password=%s&loginmode=static&wlanacssid=CMCC-EDU\
&wlanacname=%s&wlanacip=%s&wlanuserip=%s&issaveinfo=1'\
    % (username, passwd, acname, acip, userip)

temp = str(opener.open(lURL, data.encode('utf-8')).read())
cj.save()
# sURL:for going to a page contains remianing time,logout URL.
sURL = re.search(r"window.location = \\'(.+?)\\'", temp).group(1)
if sURL.find('user_status.php?') != -1:
    oURL ='http://' + serverip + ':7080/zmcc/cmcc_edu_do_logout.php'
    temp = opener.open(sURL.replace(' ', '%20')).read()
    temp = temp.decode('gbk')

    import balloon
    icopath = sys.argv[0].replace('t.py', 'icon.ico')
    ba_re = re.search(r'本月套餐已用：(.+?).0 分钟', temp).group(1)
    ba_to = re.search(r'本月套餐总量：(.+?).0 分钟', temp).group(1)
    balloon.show(icopath, ba_re, ba_to, 4 )

    for i in ['logintime', 'remaintime', 'areacode', 'productid',
              'effecttime', 'expiretime', 'kestr', 'cf', 'logonsessid']:
        vars()[i]= re.search(r'value=(.+?) type=hidden name=%s>' % i, temp)
    data = 'username=(username)&logintime=(logintime)&remaintime=(remaintime)\
&areacode=(areacode)&wlanacip=(acip)\&wlanacname=(acname)\
&wlanacssid=CMCC-EDU&wlanuserip=(userip)&productid=(productid)\
&effecttime=(effecttime)\&expiretime=(expiretime)&presenttime=\
&keystr=(keystr)&cf=(cf)&logouttype=TYPESUBMIT\
&logonsessid=(logonsessid)' % vars()
    print(vars())
    opener.open(oURL, data.encode('utf-8'))
