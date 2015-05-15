from notify2 import *

class Notifier:
    info, warning, error = range(1, 4)

    def __init__(self, icopath='', timeout=EXPIRES_DEFAULT):
        init('CMCC-EDU-autologin')
        self._timeout = timeout
        self._no = Notification('CMCC-EDU-autologin', 'logging in...', icopath)
        self._no.set_timeout(EXPIRES_NEVER)
        self._no.show()

    def show_tip(self, _type, title, body):
        icon = {self.info: 'info', self.warning: 'important',
                self.error: 'error'}[_type]
        self._no.update(title, body, icon)
        self._no.show()

    def destroy(self):
        self._no.set_timeout(self._timeout)
        self._no.show()
        

if __name__ == '__main__':
    no = Notifier()
    no.show_tip(no.info, 'aa', 'bb')
    no.destroy()

