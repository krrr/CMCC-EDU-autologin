import re
import requests
import sys
import os
import configparser

headers = {'User-agent': 'Mozilla/4.0'}
test_url = 'http://www.google.cn/favicon.ico'
errors = {'与在线用户名不一致': 'We have not been logged out',
          '密码错误': 'Wrong username or password'}
cwd = os.path.split(sys.argv[0])[0] if os.sep in sys.argv[0] else ''

# load settings
try:
    config = configparser.ConfigParser()
    config.read(os.path.join(cwd, 'config.ini'))
    username = config['Main']['Username']
    passwd = config['Main']['Password']
    timereminder_on = config['Main'].getboolean('Timereminder')
except:
    print('Error: Failed loading config file')
    sys.exit(-1)

# setup GUI
if config['GUI']['Type'] == 'Win':
    import balloon
    no = balloon.Notifier(icopath=os.path.join(cwd, 'icon.ico'),
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

    # prepare data for POST
    iurl = re.search(r'id="Wp_frame" src="(.+?)" ', r.text).group(1)
    iurlm, datastr = iurl.split('?')
    posturl = iurlm.replace('input', 'do_login')  # for HTTP post
    data = {}
    for i in datastr.split('&'):
        key, value = i.split('=')
        data[key] = value
    data.update({'loginmode': 'static',
                 'username': username, 'password': passwd})
    ipage = requests.get(iurl, timeout=7, headers=headers).text

    try:
        print('Info: get validation code')
        hidvad = re.search(r"validateid'  value='(.+?)'", ipage).group(1)
        vad = hidvad[:4]
        data.update({'loginvalidate': vad, 'loginhiddenvalidate': hidvad})
    except:
        print('Info: no validation code')
    post = requests.post(posturl, data, timeout=5, headers=headers).text

    # check if login succeed
    if 'user_status.php?' in post:
        if timereminder_on:  # Time Reminder
            # sURL:for going to a page contains remianing time,logout URL.
            surl = re.search(r"window.location = '(.+?)';", post).group(1)
            try:
                spage = requests.get(surl, timeout=5, headers=headers).text
                ba_re = re.search(r'本月套餐已用：(.+?).0 分钟', spage).group(1)
                ba_to = re.search(r'本月套餐总量：(.+?).0 分钟', spage).group(1)
                print('Succeed.Time Usage: %s/%s (min)  [used/total]' % (ba_re,ba_to))
                myprint(1, 'Cxx-autologin succeed',
                        'Time Usage: %s/%s (min)  [used/total]' % (ba_re, ba_to))
            except Exception:
                print('Succeed (Failed getting time usage)')
                myprint(1, 'Cxx-autologin succeed', 'Failed getting time usage')
        else:
            print('Succeed')
            myprint(1, '', 'Cxx autologin succeed')
        sys.exit()
    else:
        for e in errors:
            if e in post:
                print('Error: ' + errors[e])
                myprint(3, 'Cxx-autologin failed', errors[e])
                sys.exit(-1)
        raise Warning('Unknown error type')

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
    finally:
        # destrpy trayicon
        if 'no' in globals(): no.destroy()
