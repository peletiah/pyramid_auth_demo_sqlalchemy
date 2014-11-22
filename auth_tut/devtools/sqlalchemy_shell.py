import os
import sys
from code import InteractiveConsole
import readline
import atexit

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.paster import bootstrap
from pyramid.request import Request

from auth_tut.models import DBSession


class SQLAlchemyShell(InteractiveConsole):
    """A subclass of the code.InteractiveConsole class, adding a history file
    and readline support.
 
    Mac OS X Lion users may need to:
 
        sudo easy_install readline
 
    To get a readline library which isn't b0rked."""
 
    def __init__(self, locals=None, filename="<console>", histfile=None):
        if histfile is None:
            histfile = os.path.expanduser("~/.sqlalchemy-shell-history")
        InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)
        self.init_completer()
 
    def init_completer(self):
        import rlcompleter
        self.completer = rlcompleter.Completer(namespace=self.locals)
        readline.set_completer(self.completer.complete)
        if 'libedit' in readline.__doc__:
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")
 
    def init_history(self, histfile):
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history, histfile)
 
    def save_history(self, histfile):
        readline.write_history_file(histfile)

env = bootstrap('development.ini')
#engine=engine_from_config(env['registry'].settings, 'sqlalchemy.')
#DBSession.configure(bind=engine)
ic = SQLAlchemyShell()
cmd = "from auth_tut.models import *"
print ">>>", cmd
ic.push(cmd)
cmd = "import transaction"
print ">>>", cmd
ic.push(cmd)
ic.interact(banner="Use quit() or Ctrl-D (i.e. EOF) to exit")



