# .pyw for running on Windows without console.
from mainfunc import main

def print_gui(dat, path, config, sys):
    import balloon

    if 'Info' in dat: return None
    
    if 'Error' in dat or 'fail' in dat:
        tiptype = 'error'
    elif 'Warning' in dat:
        tiptype = 'warning'
    else:
        tiptype = 'info'

    dat = dat.split(': ')[-1]

    balloon.show(path + 'icon.ico',
                'CMCC-EDU-autologin',
                dat,
                tiptype=tiptype,
                timeout=int(config['GUI']['Balloontimeout']),
                winver=sys.getwindowsversion().major)

main(print_gui)
