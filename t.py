import re
import urllib.request as Urlreq
import http.cookiejar as Cookie
import sys

if '\\' in sys.argv[0]:  # Run as exe
    path = ''
else:
    path = sys.argv[0].rpartition('\\')[0] + '\\'

try:
    username = sys.argv[1]
    passwd = sys.argv[2]
except IndexError:
    print('Usage: [username] [password] [remind]/[]')
    sys.exit()

cookiejar = Cookie.LWPCookieJar(path + 'cookie.txt')
opener = Urlreq.build_opener(Urlreq.HTTPCookieProcessor(cookiejar))
opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0;\
Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.3072\
9; .NET CLR 3.0.30729; Tablet PC 2.0)'), ('Accept-Encoding', 'gzip, deflate')]

try:
    temp = str(opener.open('http://8.8.8.8').read())
except:
    print('Error: network connection is bad or network connected is not CMCC')
    sys.exit()

# iURL: for getting lURL,validates,userip,acip...
# lURL: for sending all data to login(HTTP POST).
iURL = re.search(r'<iframe class="Wp_frame" id="Wp_frame" src="(.+?)" ', temp).group(1)
lURL = iURL.partition('cmcc_edu_input.php')[0] + 'cmcc_edu_do_login.php'

userip = re.search(r'wlanuserip=(.+?)&', iURL).group(1)
acname = re.search(r'wlanacname=(.+?)&', iURL).group(1)
acip = re.search(r'wlanacip=(.+?)&', iURL).group(1)


def login_noc():
    ipage = str(opener.open(iURL).read())

    try:  # get validation code
        hidvad = re.search(r"validateid\\'  value=\\'(.+?)\\'", ipage).group(1)
        hidvad = hidvad.replace('|', '%7C')
        vad = hidvad[:4]
        data = 'username=%s&password=%s&loginvalidate=%s&loginhiddenvalidate=%s\
&loginmode=static&wlanacssid=CMCC-EDU&wlanacname=%s&wlanacip=%s\
&wlanuserip=%s&issaveinfo=1' \
               % (username, passwd, vad, hidvad, acname, acip, userip)
    except:  # no validation code
        data = 'username=%s&password=%s&loginmode=static&wlanacssid=CMCC-EDU\
&wlanacname=%s&wlanacip=%s&wlanuserip=%s&issaveinfo=1' \
               % (username, passwd, acname, acip, userip)

    lpage = opener.open(lURL, data.encode('utf-8')).read()
    return checker(lpage.decode('gbk'))


def login_c():
    cookiejar.load()
    data = 'wlanacname=%s&wlanacip=%s&wlanuserip=%s&wlanacssid=CMCC-EDU\
&loginmode=cookie' % (acname, acip, userip)

    lpage = opener.open(lURL, data.encode('utf-8')).read()
    return checker(lpage.decode('gbk'))


def checker(lpage):
    if 'user_status.php?' in lpage:
        print('Info: Login succeed')
        savecookie(lpage, lURL)
        # Time Reminder
        if 'remind' in sys.argv:
            import balloon
            # sURL:for going to a page contains remianing time,logout URL.
            surl = re.search(r"window.location = '(.+?)';", lpage).group(1)
            spage = opener.open(surl.replace(' ', '%20')).read()
            spage = spage.decode('gbk')
            icopath = path + 'icon.ico'
            ba_re = re.search(r'本月套餐已用：(.+?).0 分钟', spage).group(1)
            ba_to = re.search(r'本月套餐总量：(.+?).0 分钟', spage).group(1)
            balloon.show(icopath, ba_re, ba_to, 4)
        return 'Succeed'
    else:
        if '认证信息无效' in lpage:
            print('Error: CookieFailed')
            return 'CookieFail'
        else:
            print('Error: Login failed')
            return 'Failed'


def savecookie(lpage, lurl):
    import urllib.parse

    cookielst = re.findall(r'setCookie\("(.+)",\s*"(.+)?",\s?.?365.?\)', lpage)
    cookiedic = {i[0]: urllib.parse.quote(i[1], safe='=&') for i in cookielst}
    cookiedic['supportCookie'] = 'YES'

    lurl = lurl.replace('https://', '')
    serverip = lurl.partition(':')[0]
    cpath = '/' + lurl.partition('/')[2]

    with open(path + 'cookie.txt', 'w') as cookiefile:
        cookiefile.write('#LWP-Cookies-2.0\n')
        for i in cookiedic:
            cookiefile.write('Set-Cookie3: %s=%s; path="%s"; \
domain="%s"; path_spec; expires="2015-10-10 05:17:57Z"; \
httponly=None; version=0\n' % (i, cookiedic[i], cpath, serverip))


try:
    cookiejar.load()
    print('Info: Using Cookie')
    if login_c() == 'CookieFail':
        login_noc()
except:
    login_noc()