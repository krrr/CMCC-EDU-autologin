import re
import urllib.request as Urlreq
import http.cookiejar as Cookie
import sys
import os
import configparser

def main(printfunc=print):
    """GUI disabled when print function is built-in one"""
    if os.sep not in sys.argv[0]:  # Run as exe
        path = ''
    else:
        path = os.path.split(sys.argv[0])[0] + os.sep

    try:
        config = configparser.ConfigParser()
        config.read(path + 'config.ini')
        username = config['Main']['Username']
        passwd = config['Main']['Password']
        timereminder_on = config['Main'].getboolean('Timereminder')
        
        if 'built-in' not in str(printfunc):  # GUI enabled
            def myprint(dat): printfunc(dat,path,config,sys)
        else:
            myprint = printfunc
    except:
        print('Error: Failed loading config file')
        sys.exit()

    cookiejar = Cookie.LWPCookieJar(path + 'cookie.txt')
    opener = Urlreq.build_opener(Urlreq.HTTPCookieProcessor(cookiejar))
    opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0;\
Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.3072\
9; .NET CLR 3.0.30729; Tablet PC 2.0)')]

    try:
        temp = str(opener.open('http://8.8.8.8', timeout=8).read())
    except:
        try:
            temp = opener.open('http://www.google.cn/favicon.ico', timeout=5)
        except:  # no internet connection
            myprint('Error: network connection is bad or network connected is not CMCC')
        finally:
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
        return checker(lpage.decode('gbk'), False)


    def login_c():
        cookiejar.load()
        data = 'wlanacname=%s&wlanacip=%s&wlanuserip=%s&wlanacssid=CMCC-EDU\
&loginmode=cookie' % (acname, acip, userip)

        lpage = opener.open(lURL, data.encode('utf-8')).read()
        return checker(lpage.decode('gbk'), True)


    def checker(lpage, is_c):
        if 'user_status.php?' in lpage:
            # skip saving cookie when login successfully by cookie
            if not is_c: savecookie(lpage, lURL)
            if timereminder_on:  # Time Reminder
                # sURL:for going to a page contains remianing time,logout URL.
                surl = re.search(r"window.location = '(.+?)';", lpage).group(1)
                spage = opener.open(surl.replace(' ', '%20')).read()
                spage = spage.decode('gbk')
                ba_re = re.search(r'本月套餐已用：(.+?).0 分钟', spage).group(1)
                ba_to = re.search(r'本月套餐总量：(.+?).0 分钟', spage).group(1)
                myprint('Time Usage: %s/%s (min)  [used/total]' % (ba_re,ba_to))
            else:
                myprint('Login succeed')
                
            return 'Succeed'
        else:
            if '认证信息无效' in lpage:
                myprint('Warning: CookieFailed')
                return 'CookieFail'
            else:
                edic = {'与在线用户名不一致': 'Error: We have not been logged out',
                        '密码错误': 'Error: Wrong username or password'}
                for e in edic:
                    if e in lpage:
                        myprint(edic[e])
                        return 'Failed'

    def savecookie(lpage, lurl):
        """Parse javascript in lpage and save the cookie to cookie.txt"""
        import urllib.parse

        cookielst = re.findall(r'setCookie\("(.+)",\s*"(.+)?",\s?.?365.?\)', lpage)
        cookiedic = {i[0]: urllib.parse.quote(i[1], safe='=&') for i in cookielst}
        cookiedic['supportCookie'] = 'YES'

        lurl = lurl.replace('https://', '')
        serverip = lurl.partition(':')[0]
        cpath = '/' + lurl.partition('/')[2]

        cookiefile = open(path + 'cookie.txt', 'w')
        cookiefile.write('#LWP-Cookies-2.0\n')
        for i in cookiedic:
            cookiefile.write('Set-Cookie3: %s=%s; path="%s"; \
domain="%s"; path_spec; expires="2017-10-10 05:17:57Z"; \
httponly=None; version=0\n' % (i, cookiedic[i], cpath, serverip))
        cookiefile.close()

    try:
        cookiejar.load()
        myprint('Info: Using Cookie')
    except:
        login_noc()
    else:
        if login_c() == 'CookieFail': login_noc()