# Modified from Pyzen and  gingerprawn.The license of gingerprawn is GPLv3.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


from ctypes import *
from ctypes.wintypes import *
from time import sleep

# reference
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms648045%28v=vs.85%29.aspx (LoadImage function)
# http://msdn.microsoft.com/en-us/library/windows/desktop/bb773352%28v=vs.85%29.aspx (NOTIFYICONDATA structure)

Shell_NotifyIcon = windll.shell32.Shell_NotifyIconW
LoadImage = windll.user32.LoadImageW


class GUID(Structure):
    _fields_ = [
            ('Data1', c_uint32),
            ('Data2', c_uint16),
            ('Data3', c_uint16),
            ('Data4', c_ubyte * 8),
            ]


class NOTIFYICONDATA(Structure):
    _fields_ = [
            ('cbSize', DWORD),
            ('hWnd', HWND),
            ('uID', UINT),
            ('uFlags', UINT),
            ('uCallbackMessage', UINT),
            ('hIcon', HICON),
            ('szTip', c_wchar * 128),
            ('dwState', DWORD),
            ('dwStateMask', DWORD),
            ('szInfo', c_wchar * 256),
            ('uTimeout', UINT), # Also is uVersion
            ('szInfoTitle', c_wchar * 64),
            ('dwInfoFlags', DWORD),
            ('guidItem', GUID),
            ('hBalloonIcon', HICON),
            ]

tiptypedic = {'info':1, 'error':3}

def show(title, body, tiptype='info', timeout=5, winver=6):
    path = __file__.rpartition('\\')[0]+'\\icon.ico'
    path = path.replace('\\', r'\\')

    if winver >= 6: # Windows Vista and later
        cbsize = sizeof(NOTIFYICONDATA)
    else: # Ingore lower OS than Windows XP
        cbsize = 952

    nid = NOTIFYICONDATA(
            cbSize=cbsize,
            hWnd=0,
            uID=0,
            uFlags=2|16|128, #NIF_ICON | NIF_INFO | NIF_SHOWTIP
            szInfo=body,
            szInfoTitle=title,
            hIcon=LoadImage(None, path, 1, 16, 16, 0x10),
            dwInfoFlags=tiptypedic[tiptype]
            )
    Shell_NotifyIcon(0, byref(nid)) # NIM_ADD
    sleep(timeout)
    Shell_NotifyIcon(2, byref(NOTIFYICONDATA(hWnd=0, uID=0))) # NIM_DELETE

if __name__ == '__main__':
    show('Title', 'Body','error', timeout=1)
    show('Title', 'Body', timeout=1)