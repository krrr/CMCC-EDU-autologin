import re
import urllib.request as urlreq
import http.cookiejar
import sys
import balloon

username = ''
passwd = ''

cj = http.cookiejar.LWPCookieJar('cookie.txt')
opener = urlreq.build_opener(urlreq.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Tablet PC 2.0)')]

temp = str(opener.open('http://g.cn').read())
# iURL: for getting lURL,validates,userip,acip... 
# lURL: for sending username,pass,all.
iURL = re.search(r'<iframe class="Wp_frame" id="Wp_frame" src="(.+?)" ', temp).group(1)
lURL = 'https://' + re.search(r'https://(.+?):', iURL).group(1) + ':7090/zmcc/cmcc_edu_do_login.php'

userip = re.search(r'wlanuserip=(.+?)&', iURL).group(1)
acname = re.search(r'wlanacname=(.+?)&', iURL).group(1)
acip = re.search(r'wlanacip=(.+?)&', iURL).group(1)

temp = str(opener.open(iURL).read())
try:  # get validation code
    hidvad = re.search(r"validateid\\'  value=\\'(.+?)\\'", temp).group(1)
    vad = hidvad[:4]
    hidvad = hidvad.replace('|', '%7C')
    data = 'username=%s&password=%s&loginvalidate=%s&loginhiddenvalidate=%s&loginmode=static&wlanacssid=CMCC-EDU&wlanacname=%s&wlanacip=%s&wlanuserip=%s&issaveinfo=' % (username,passwd,vad,hidvad,acname,acip,userip)
except:  # no validation code
    data = 'username=%s&password=%s&loginmode=static&wlanacssid=CMCC-EDU&wlanacname=%s&wlanacip=%s&wlanuserip=%s&issaveinfo=' % (username,passwd,acname,acip,userip)

temp = str(urlreq.urlopen(lURL, data.encode('utf-8')).read())
# sURL:for going to a page contains remianing time,logout URL.
sURL = re.search(r"window.location = \\'(.+?)\\'", temp).group(1)
