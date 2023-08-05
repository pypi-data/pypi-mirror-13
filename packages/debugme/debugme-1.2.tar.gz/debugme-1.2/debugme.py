import code
import inspect
import readline
import rlcompleter
import sys
from pprint import pprint
sys.displayhook = pprint

frame = inspect.currentframe()
while True:
    module = inspect.getmodule(frame)
    in_importlib = not module and 'importlib' in frame.f_code.co_filename
    if not in_importlib and module.__name__ != 'debugme':
        break
    frame_, frame = frame, frame.f_back
    del(frame_)

vars = frame.f_globals
vars.update(frame.f_locals)
del(frame)

class debugme: exit = True
vars['debugme'] = debugme()

readline.set_completer(rlcompleter.Completer(vars).complete)
readline.parse_and_bind("tab: complete")
shell = code.InteractiveConsole(vars)
shell.interact()
if vars['debugme'].exit:
    sys.exit(1)
