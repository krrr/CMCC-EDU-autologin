#!/usr/bin/env python3
import re
import requests
import sys
import os
import configparser
from bs4 import BeautifulSoup
from urllib.parse import unquote
from requests.exceptions import Timeout, ConnectionError


headers = {'User-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_2 like Mac OS X) ' +
                         'AppleWebKit/601.1 (KHTML, like Gecko) CriOS/47.0.2526.70 ' +
                         'Mobile/13C71 Safari/601.1.46'}
test_url = 'http://23.201.102.83/'
status_re = re.compile(r'(\d+)分钟（其中校园\d+分钟）,(\d+)MB')
meta_refresh_re = re.compile(r'''<meta\s+http-equiv=["']refresh["']\s+content=["']0;url=(.+)["']''')
err_msg_re = re.compile(r'alert\("(.+)"\);')

fdir = os.path.dirname(os.path.realpath(__file__))
icopath = os.path.join(fdir, 'cmcc-logo.ico')


# load settings
try:
    config = configparser.ConfigParser()
    config.read(os.path.join(fdir, 'config.ini'), encoding='utf-8')
    username = config['Main']['Username']
    passwd = config['Main']['Password']
    timeout = int(config['GUI']['BalloonTimeout'])
except Exception as e:
    print('Error: Failed to load config file %s' % e)
    sys.exit(-1)

# setup GUI
no, tip = None, lambda *args: None
if config['GUI']['Enable'] in ('True', 'true', '1'):
    if sys.platform == 'win32':
        import balloon
        no = balloon.Notifier(icopath, timeout)
        tip = no.show_tip
    else:
        try:
            import balloonunix
        except ImportError:
            no, tip = None, lambda *args: None
            print('Error: cannot import notify2')
        else:
            no = balloonunix.Notifier(icopath, timeout*1000)  # timeout is in ms
            tip = no.show_tip


def get_post_url_data(page):
    soup = BeautifulSoup(page, 'html.parser')
    html_title = soup.title.string
    is_cmcc = any((i in html_title) for i in ('移动', 'WLAN', 'CMCC'))
    error = ValueError("移动又改页面了，脚本报废" if is_cmcc else "非CMCC-EDU登陆页")

    if not is_cmcc or soup.form is None:
        raise error

    url = soup.form['action']
    print('Debug: post-url: %s' % url)

    data = {i['name']: i.attrs.get('value') for i in soup.form.find_all('input')}

    if any(i not in data for i in ('ssid', 'userName', 'userPwd')):
        raise error
    if data['ssid'] != 'CMCC-EDU':
        print('Warning: SSID: %s' % data['ssid'])

    data.update({'userName': username, 'userPwd': passwd})
    print('Debug: post-data: %s' % data)
    return url, data


def get_status(page):
    soup = BeautifulSoup(page, 'html.parser')

    used_s = unquote(soup.form.find('input', {"name": "usedFree"})['value'])
    total_s = unquote(soup.form.find('input', {"name": "freePkgTotal"})['value'])

    used_match = status_re.match(used_s)
    used_minute, used_mb = used_match.group(1), used_match.group(2)
    total_match = status_re.match(total_s)
    total_minute, total_mb = total_match.group(1), total_match.group(2)

    if total_mb == '0':
        used, total = used_minute, total_minute
        unit = '分钟'
    else:
        used, total = used_mb, total_mb
        unit = 'MB'

    return used, total, unit


def main():
    if not username or not passwd:
        print('username or password is empty')
        sys.exit(-1)
    # check network environment
    r = requests.get(test_url, timeout=4, headers=headers)
    if r.url == test_url:
        print('Internet connection works, exit silently.')
        sys.exit()
    else:
        print('start login progress')

    # 要跟一个莫名其妙的跳转
    match = meta_refresh_re.search(r.text)
    if match:
        print('Debug: follow meta tag redirect: %s' % match.group(1))
        r = requests.get(match.group(1), timeout=4, headers=headers)

    # prepare data for POST, deal with iframe
    try:
        post_url, data = get_post_url_data(r.text)
    except ValueError as e:
        tip(no.error, 'Cxx-autologin 错误', str(e))
        sys.exit(-1)

    post = requests.post(post_url, data, timeout=4, headers=headers).text

    # check if login succeed
    if 'portalLoginRedirect' in post:
        print('Succeed')
        tip(no.info, 'Cxx-autologin 登陆成功', '用量：%s/%s %s' % get_status(post))
        sys.exit()
    else:
        match = err_msg_re.search(post)
        if match:
            print('Error: ' + match.group(1))
            tip(no.error, 'Cxx-autologin 错误', match.group(1))
            sys.exit(-1)
        else:
            with open(os.path.join(fdir, 'error_page.html'), 'w', encoding='utf-8') as f:
                f.write(post)
            raise Exception('Unknown error')


def test():
    """
    http://211.138.125.52:7080/zmcc/index.php?wlanacname=0049.0579.571.00&wlanuserip=10.245.12.209&ssid=CMCC-EDU&nasip=211.140.146.234
    https://211.138.125.52:7090/zmcc/indexForce.wlan?wlanacname=0049.0579.571.00&wlannasid=&wlanuserip=10.245.12.209&ssid=CMCC-EDU&nasip=211.140.146.234&usermac=
    """
    with open('test/login_page_sample.htm', encoding='utf-8') as f:
        post_url, data = get_post_url_data(f.read())
        assert post_url == 'https://211.138.125.52:7090/zmcc/portalLogin.wlan?1491109121400'
        assert data == {'wlanAcName': '0049.0579.571.00', 'wlanUserIp': '10.245.12.209',
                        'wlanAcIp': '', 'verifyHidden': '', 'userPwd': '', 'ssid': 'CMCC-EDU',
                        'autosaveuserinfo': 'yes', '_userPwd': '输入固定密码/临时密码',
                        'verifyCode': '', 'issaveinfo': '', 'userName': ''}

    with open('test/success_redirect_sample.htm', encoding='utf-8') as f:
        assert get_status(f.read()) == ('92', '15000', '分钟')


if __name__ == '__main__':
    try:
        main()
    except (Timeout, ConnectionError):
        print('Error: Bad network connection')
        tip(no.error, 'Cxx-autologin 错误', '网络超时')
    except Exception as e:
        print('Error: %s)' % str(e))
        tip(no.error, 'Cxx-autologin 未捕捉异常', str(e))
    finally:
        if no: no.destroy()
