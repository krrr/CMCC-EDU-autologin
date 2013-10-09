import re
import urllib.request as urlreq
import urllib.parse as urlpar
import http.cookiejar
import sys

username = '18395920713'
passwd = 'Syb3I4'

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
if sURL.find('user_status.php?') != -1: # login succeed
    oURL ='http://' + serverip + ':7080/zmcc/cmcc_edu_do_logout.php'
    temp = opener.open(sURL.replace(' ', '%20')).read()
    temp = temp.decode('gbk')

    import balloon
    icopath = sys.argv[0].replace('t.py', 'icon.ico')
    ba_re = re.search(r'本月套餐已用：(.+?).0 分钟', temp).group(1)
    ba_to = re.search(r'本月套餐总量：(.+?).0 分钟', temp).group(1)
    balloon.show(icopath, ba_re, ba_to, 4)

    def logout(oURL, oURLpage):
        datadic = {}
        for i in ['logintime', 'remaintime', 'areacode', 'productid',
                  'effecttime', 'expiretime', 'keystr', 'cf', 'logonsessid']:
            try:
                datadic[i] = re.search(r"<input type='hidden' name='%s'(\s+?)value='(.+?)'>" % i, oURLpage).group(2)
            except AttributeError:
                datadic[i] = ''

        datadic.update(vars())
        data = 'username=%(username)s&logintime=%(logintime)s&remaintime=%(remaintime)s\
    &areacode=%(areacode)s&wlanacip=%(acip)s&wlanacname=%(acname)s\
    &wlanacssid=CMCC-EDU&wlanuserip=%(userip)s&productid=%(productid)s\
    &effecttime=%(effecttime)s&expiretime=%(expiretime)s&presenttime=\
    &keystr=%(keystr)s&cf=%(cf)s&logouttype=TYPESUBMIT\
    &logonsessid=%(logonsessid)s' % datadic
        data = urlpar.quote_plus(data, safe='=&')
        opener.open(oURL, data.encode('utf-8'))

else:
    print('login failed')