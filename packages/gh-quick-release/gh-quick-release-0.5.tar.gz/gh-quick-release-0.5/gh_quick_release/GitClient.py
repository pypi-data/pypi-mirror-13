from subprocess import call, check_output, STDOUT
from os import devnull

class GitClient:
    def __init__(self, redirect):
        self.redirect = redirect

    def _arr(self, tpl):
        arr = []
        for item in tpl:
            arr.append(item)
        return arr

    def check_output(self, *params):
        args = self._arr(('git',) + params)
        return check_output(args)

    def call(self, params):
        args = self._arr(('git',) + params)

        code = 0
        if not self.redirect:
            code = call(args)
        else:
            with open(devnull, 'w') as n:
                code = call(args, stdout=n, stderr=STDOUT)
        if code != 0:
            cmd = ' '.join(args)
            raise RuntimeError('Git command "' + cmd + '" failed')

    def push(self, *params):
        self.call(('push',) + params)

    def commit(self, *params):
        self.call(('commit',) + params)

    def add(self, *params):
        self.call(('add',) + params)

    def checkout(self, *params):
        self.call(('checkout',) + params)

    def merge(self, *params):
        self.call(('merge',) + params)
