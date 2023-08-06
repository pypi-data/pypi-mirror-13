import sys, code, re
from jokes.core.console import Console as jokesConsole
from io import StringIO
from contextlib import contextmanager

@contextmanager
def std_redirector(stdin=sys.stdin, stdout=sys.stdin, stderr=sys.stderr):
    tmp_fds = stdin, stdout, stderr
    orig_fds = sys.stdin, sys.stdout, sys.stderr
    sys.stdin, sys.stdout, sys.stderr = tmp_fds
    yield
    sys.stdin, sys.stdout, sys.stderr = orig_fds

class PyShell(code.InteractiveConsole):
    def __init__(self, locals=None):
        code.InteractiveConsole.__init__(self, locals=locals)
        self.output = StringIO()
        self.ps1 = getattr(sys, "ps1", ">>> ")
        self.ps2 = getattr(sys, "ps2", "... ")
        self.banner = ("Python %s\n%s\n" % (sys.version, sys.platform) +
                       'Type "help", "copyright", "credits" or "license" '
                       'for more information.\n')
    
    def push(self, command): 
        if not (True in [ bool(re.match(pattern, command)) for pattern in ['exit\(\)', ] ]): #Check for forbidden command regex patterns
            self.output = StringIO()
            with std_redirector(stdout=self.output, stderr=self.output):
                try:
                    more = code.InteractiveConsole.push(self, command)
                    result = self.output.getvalue()
                except (SyntaxError, OverflowError):
                    pass
                return more, result
        else:
            return False, '"'+command+'" is a forbidden command in this version of the python interpreter'

INTERPRETER_LANGUAGES = ['python', 'javascript', 'jokes']
class Interpreter():
    def __init__(self, language='python'):
        self.set_language(language)
        
    def set_language(self, language):
        if language in INTERPRETER_LANGUAGES:
            self.language = language
            self.set_interpreter(language)
    
    def set_interpreter(self, language):
        """ Called within self.set_language() method """
        if language == 'python':
            self.interpreter = PyShell()
        elif language == 'jokes':
            self.interpreter = jokesConsole()
        
    def input(self, inputstring):
        """ Do something and return a dict {'concat': bool, 'print': str} """
        return getattr(self, 'input_'+self.language)(inputstring)
    
    def input_python(self, inputstring):
        """ Run inputstring as shell command and return a dict {'concat': bool, 'print': str} """
        result = self.interpreter.push(inputstring)
        return {'concat':result[0], 'print':result[1]}
    
    def input_jokes(self, inputstring):
        """ Run inputstring as shell command and return a dict {'concat': bool, 'print': str} """
        result = self.interpreter.push(inputstring)
        return {'concat':result[0], 'print':result[1]}