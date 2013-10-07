"For Windows only.Using PowerShell Script to show balloon in system tray"
import subprocess
def show(used, total, showtime):
    ps = '''[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
    $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
    $objNotifyIcon.Icon = "icon.ico"
    $objNotifyIcon.BalloonTipIcon = "Info"
    $objNotifyIcon.BalloonTipText = "%smin (used)/%smin (total)"
    $objNotifyIcon.BalloonTipTitle = "Time reminder"
    $objNotifyIcon.Visible = $True
    $objNotifyIcon.ShowBalloonTip(1000)
    Sleep %s
    $objNotifyIcon.Visible = $False
    exit''' % (used, total, showtime)

    subprocess.Popen(['powershell.exe', ps])