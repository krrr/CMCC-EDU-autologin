"For Windows only.Using PowerShell Script to show balloon in system tray"
import subprocess
def show(time):
    used, total = time
    ps = '''[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
    $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
    $objNotifyIcon.Icon = "icon.ico"
    $objNotifyIcon.BalloonTipIcon = "Info"
    $objNotifyIcon.BalloonTipText = "%s/%s."
    $objNotifyIcon.BalloonTipTitle = "TEST"
    $objNotifyIcon.Visible = $True
    $objNotifyIcon.ShowBalloonTip(1000)
    Sleep 2
    $objNotifyIcon.Visible = $False
    exit''' % (used, total)

    subprocess.Popen(['powershell.exe', ps])