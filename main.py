#!/usr/bin/env python3
import re
import requests
from requests.exceptions import Timeout, ConnectionError
import sys
import os
import configparser

headers = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 8.0;)'}
test_url = 'http://23.201.102.83/'
errors = {'与在线用户名不一致': 'We have not been logged out',
          '已在线': 'We have not been logged out',
          '密码错误': 'Wrong username or password',
          '登录认证失败': 'Please reconnect WLAN'}
fdir = os.path.dirname(os.path.realpath(__file__))
icopath = os.path.join(fdir, 'cmcc-logo.ico')
form_exp = re.compile(r'''<input.+name=["'](wlanAcName|wlanAcIp|wlanUserIp|ssid|verifyHidden|'''
                      '''idissaveinfo|passType)["'].+value=["']([^'"]*)["'].+/>''')


# load settings
try:
    config = configparser.ConfigParser()
    config.read(os.path.join(fdir, 'config.ini'))
    username = config['Main']['Username']
    passwd = config['Main']['Password']
    timeout = int(config['GUI']['BalloonTimeout'])
except Exception:
    print('Error: Failed to load config file')
    sys.exit(-1)

# setup GUI
if config['GUI']['Type'] == 'Win':
    import balloon
    no = balloon.Notifier(icopath, timeout)
    tip = no.show_tip
elif config['GUI']['Type'] == 'Unix':
    try:
        import balloonunix
    except ImportError:
        no, tip = None, lambda *args: None
        print('Error: cannot import notify2')
    else:
        no = balloonunix.Notifier(icopath, timeout*1000)  # timeout is in ms
        tip = no.show_tip
else:
    no, tip = None, lambda *args: None


def main():
    # check network environment
    r = requests.get(test_url, timeout=4, headers=headers)
    if r.url == test_url:
        print('Internet connection works, exit silently.')
        sys.exit()
    else:
        print('start login progress')

    # prepare data for POST, deal with iframe
    ipage = r.text
    match = re.search(r'''<form.+method='post' action="(.+?)">''', ipage)
    if match is None:
        tip(no.error, 'Cxx-autologin failed', 'not CMCC-EDU protal!')
        sys.exit(-1)
    posturl = match.group(1)
    print('Debug: post-url: %s' % posturl)
    data = {'userName': username, 'userPwd': passwd}
    for l in ipage.split('\n'):
        s = form_exp.search(l)
        if s:
            data[s.group(1)] = s.group(2)
    print('Debug: post-data: %s' % data)
    post = requests.post(posturl, data, timeout=4, headers=headers).text

    # check if login succeed
    if 'portalLoginRedirect' in post:
        print('Succeed')
        tip(no.info, '', 'Cxx-autologin succeed')
        sys.exit()
    else:
        for e in errors:
            if e in post:
                print('Error: ' + errors[e])
                tip(no.error, 'Cxx-autologin failed', errors[e])
                sys.exit(-1)
        else:
            with open(os.path.join(fdir, 'error_page.html'), 'w', encoding='utf-8') as f:
                f.write(post)
            raise Exception('Unknown error')

if __name__ == '__main__':
    try:
        main()
    except (Timeout, ConnectionError):
        print('Error: Bad network connection')
        tip(no.error, 'Cxx-autologin failed', 'Bad network connection')
    except Exception as e:
        print('Error: %s)' % str(e))
        tip(no.error, 'Cxx-autologin dead', 'We found a new bug: %s' % str(e))
    finally:
        if no: no.destroy()
