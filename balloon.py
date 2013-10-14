"For Windows only.Using PowerShell Script to show balloon in system tray"
import subprocess
def show(icopath, used, total, showtime):
    ps = '''[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
    $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
    $objNotifyIcon.Icon = "%s"
    $objNotifyIcon.BalloonTipIcon = "Info"
    $objNotifyIcon.BalloonTipText = "%s/%s (min)  [used/total]"
    $objNotifyIcon.BalloonTipTitle = "Time reminder"
    $objNotifyIcon.Visible = $True
    $objNotifyIcon.ShowBalloonTip(1000)
    Sleep %s
    $objNotifyIcon.Visible = $False
    exit''' % (icopath, used, total, showtime)
    
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


    subprocess.Popen(['powershell.exe', ps], startupinfo=startupinfo)