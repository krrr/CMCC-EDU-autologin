"""Display balloon tip on Windows.
This module provides a class that display a tray icon and show balloon tip
by calling win32api directly.
Bug: tray icon will disappear when cursor moving over."""

# Modified from Pyzen and gingerprawn. The license of gingerprawn is GPLv3.
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

import sys
from ctypes import *
from ctypes.wintypes import *
from time import sleep

# References
# LoadImage function:
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms648045%28v=vs.85%29.aspx
# NOTIFYICONDATA structure:
# http://msdn.microsoft.com/en-us/library/windows/desktop/bb773352%28v=vs.85%29.aspx

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
        ('uTimeout', UINT),  # Also is uVersion
        ('szInfoTitle', c_wchar * 64),
        ('dwInfoFlags', DWORD),
        ('guidItem', GUID),
        ('hBalloonIcon', HICON),
    ]


class Notifier:
    info, warning, error = range(1, 4)  # also dwInfoFlags
    
    def __init__(self, icopath='', timeout=0):
        winver = sys.getwindowsversion().major
        icopath = icopath.replace('\\', '\\\\')
        self.timeout = timeout
        if winver >= 6:  # Windows Vista and later
            cbsize = sizeof(NOTIFYICONDATA)
        else:            # Ignore version lower than XP
            cbsize = 952
        self.data = NOTIFYICONDATA(
            cbSize=cbsize,
            hWnd=0,
            uID=0,
            uFlags=2,  # NIF_ICON
            hIcon=LoadImage(None, icopath, 1, 16, 16, 0x10),
            )
        Shell_NotifyIcon(0, byref(self.data))  # NIM_ADD

    def destroy(self):
        return Shell_NotifyIcon(2, byref(self.data))  # NIM_DELETE

    def show_tip(self, type, title, body):
        self.data.szInfo = body
        self.data.szInfoTitle = title
        self.data.dwInfoFlags = type
        self.data.uFlags = 2|16|128  # NIF_ICON | NIF_INFO | NIF_SHOWTIP
        code = Shell_NotifyIcon(1, byref(self.data))  # NIM_MODIFY
        if self.timeout: sleep(self.timeout)
        return code


if __name__ == '__main__':
    no = Notifier()
    assert no.show_tip(no.error, 'aa', 'bb') == 1
    sleep(3)
    no.destroy()

