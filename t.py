import re
import requests
import sys
import os
import configparser

headers = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 8.0;)'}
test_url = 'http://www.msftncsi.com/'
errors = {'与在线用户名不一致': 'We have not been logged out',
          '已在线': 'We have not been logged out',
          '密码错误': 'Wrong username or password',
          '登录认证失败': 'Please reconnect WLAN'}
fdir = os.path.dirname(os.path.realpath(__file__))
form_exp = re.compile(r'''<input.+name=["'](.+?)["'].+value=["'](.*?)["'] />''')

# load settings
try:
    config = configparser.ConfigParser()
    config.read(os.path.join(fdir, 'config.ini'))
    username = config['Main']['Username']
    passwd = config['Main']['Password']
except Exception:
    print('Error: Failed loading config file')
    sys.exit(-1)

# setup GUI
if config['GUI']['Type'] == 'Win':
    import balloon
    no = balloon.Notifier(icopath=os.path.join(fdir, 'icon.ico'),
                          timeout=int(config['GUI']['Balloontimeout']),
                          winver=sys.getwindowsversion().major)
    def myprint(*args): no.show_tip(*args)
else:
    def myprint(*args): pass

def main():
    # check network enviroment
    r = requests.get(test_url, timeout=6, headers=headers)
    if r.url == test_url:
        print('Internet connection works,exit silently.')
        sys.exit()
    else:
        print('Info: start login progress')
    # prepare data for POST, deal with iframe and interesting names
    iurl = re.search(r'id="Wp_frame" src="(.+?)" ', r.text).group(1)
    ipage = requests.get(iurl, timeout=7, headers=headers).text
    posturl = re.search('<form.+action="(.+?)">', ipage).group(1)
    data = {'userName': username, 'userPwd': passwd}
    for l in ipage.split('\n'):
        s = form_exp.search(l)
        if s:
            data[s.group(1)] = s.group(2)
    post = requests.post(posturl, data, timeout=5, headers=headers).text
    # check if login succeed
    if 'portalLoginRedirect' in post:
        print('Succeed')
        myprint(1, '', 'Cxx autologin succeed')
        sys.exit()
    else:
        for e in errors:
            if e in post:
                print('Error: ' + errors[e])
                myprint(3, 'Cxx-autologin failed', errors[e])
                sys.exit(-1)
        else:
            with open('error_page', 'w', encoding='utf-8') as f:
                f.write(post)
            raise Exception('Unknown error type')

if __name__ == '__main__':
    try:
        main()
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        print('Error: Bad network connection')
        myprint(3, 'Cxx-autologin failed', 'Bad network connection')
        sys.exit(-1)
    except Exception as e:
        print('Error: Unknown error (%s)' % str(e))
        myprint(2, 'Cxx-autologin dead', 'We found a new bug: %s' % str(e))
        raise
    finally:  # destrpy trayicon
        if 'no' in globals(): no.destroy()
