import signal
import sys
import time
import os
import timeit

from copy import copy
from abc import abstractmethod
from bdb import BdbQuit
from codeop import compile_command

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.util import *
from karmadbg.dbgcore.nativedbg import NativeDebugger
from karmadbg.dbgcore.pydebug import PythonDebugger
from karmadbg.dbgcore.macro import *

import pykd
from pykd import *

dbgserver = None

class DebugServer(object):

    def __init__(self):
        self.pythonRunCode = False

    def startServer(self):

        global dbgserver
        dbgserver = self

        signal.signal( signal.SIGINT, signal.SIG_IGN)

        self.clientOutput = self.getClientOutput()

        sys.stdin = self
        sys.stdout = self
        sys.stderr = self

        self.nativeDbg = NativeDebugger(self)
        self.pythonDbg = PythonDebugger(self)

        self.interruptServer = self.processServerInterrupt(self)
        self.commandServer = self.processServerCommand(self)

        registerMacros()

        print
        print "start debug server"
        self.startup()

        self.nativeCommandLoop()


    def pythonCommandLoop(self):
        self.commandServer.sendAnswer(None)
        self.commandLoop(self.pythonDbg)

    def nativeCommandLoop(self):
        self.commandLoop(self.nativeDbg)

    def commandLoop(self, commandHandler):

        commandHandler.outputPrompt()

        while not self.commandServer.stopped:

            methodName, args, kwargs = self.commandServer.getRequest()

            try:

                if methodName == 'quit':
                    self.quit()
                    self.commandServer.sendAnswer(None)
                    continue

                if methodName == 'debugCommand':
                    if self.debugCommand(commandHandler, *args, **kwargs):
                        return
                    self.commandServer.sendAnswer(None)
                    commandHandler.outputPrompt()
                    continue

                if methodName == 'callFunction':
                    try:
                        result = args[0](*args[1:],**kwargs)
                    except Exception, ex:
                        result = ex
                    self.commandServer.sendAnswer(result)
                    continue

                if methodName == 'startup':
                    self.startup()
                    self.commandServer.sendAnswer(None)
                    continue
 
                # Native DBG command ( windbg )
                if hasattr(self.nativeDbg, methodName):
                    res = getattr(self.nativeDbg, methodName)(*args, **kwargs)
                    self.commandServer.sendAnswer(res)
                    continue

                # Python DBG command 
                if hasattr(self.pythonDbg, methodName):
                    res = getattr(self.pythonDbg, methodName)(*args, **kwargs)
                    self.commandServer.sendAnswer(res)
                    continue

                self.commandServer.sendAnswer(None)

            except:

                sys.stderr.write(showtraceback( sys.exc_info(), 2 ))
                self.commandServer.sendAnswer(None)

    def debugCommand(self, commandHandler, commandStr):

        if not commandStr:
            return False

        if commandHandler is self.nativeDbg:

            if self.nativeDbg.debugCommand(commandStr):
                return

            if self.isMacroCmd(commandStr):
                self.macroCmd(commandStr)
                return

            self.pythonCommand(commandStr)

            return False

        elif commandHandler is self.pythonDbg:

            return self.pythonDbg.debugCommand(commandStr)

    def write(self,str):
        self.clientOutput.output(str)

    def readline(self):
        return self.clientOutput.input()

    def flush(self):
        pass

    def breakin(self):

        if self.pythonRunCode == True:
            if self.pythonDbg.breakin():
                return
        self.nativeDbg.breakin()

    def quit(self):
        self.interruptServer.stop()
        self.commandServer.stop()

    def isMacroCmd(self,commandStr):
        return commandStr[0] == '%'

    def macroCmd(self,commandStr):

        try:
           macroCommand(commandStr)
        except SystemExit:
            print "macro command raised SystemExit"
        except:
            print showtraceback(sys.exc_info())

    def runCodeCommand(self, scriptname, args, debug = False):

        argv = sys.argv
        syspath = sys.path

        dirname, _ = os.path.split(scriptname)

        if not dirname:
            script, suffix = os.path.splitext(scriptname)
            try:
                _,fileName,desc=imp.find_module(script)
            except ImportError:
                sys.stderr.write("module \'%s\' not found\n" % script)
                self.commandServer.sendAnswer(None)
                return
        else:
            sys.path.append(dirname)

        self.pythonRunCode = True

        try:
            
            sys.argv = []
            sys.argv.append(scriptname)
            sys.argv.extend(args)

            import __builtin__

            glob = {}
            glob['__builtins__'] = __builtin__
            glob["__name__"] = "__main__"
            glob["__file__"] = scriptname
            glob["__doc__"] = None
            glob["__package__"] = None

            if debug:
                self.pythonDbg.execfile(scriptname,glob,glob)
            else:
                execfile(scriptname, glob, glob)

        except SystemExit:
            print "script raised SystemExit"

        except:
            sys.stderr.write(showtraceback( sys.exc_info(), 2 ))

        self.pythonRunCode = False

        sys.argv = argv
        sys.path = syspath

        sys.stdin = self
        sys.stdout = self
        sys.stderr = self


    def execCode(self, codestr, debug = False):

        if not codestr:
            return

        self.pythonRunCode = True

        try:

            codeObject = compile(codestr, "<input>", "single")

            if debug:
                self.pythonDbg.execcode(codeObject, globals(), globals())
            else:
                exec codeObject in globals()

        except SystemExit:
            print "expression raised SystemExit"

        except:
            print showtraceback( sys.exc_info(), 2 )

        self.pythonRunCode = False

    def timeCommand(self, command):
        t1 = time.clock()
        ret = self.nativeDbg.debugCommand(" ".join(vars[1:]))
        t2 = time.clock()
        print "time elapsed: %fs" % (t2-t1)
        return ret

    def pythonCommand(self, commandStr):

        code = None
        try:
            while True:
                code = compile_command(commandStr, "<input>", "single")
                if code:
                    break
                commandStr += "\n" + raw_input('...')

        except SyntaxError:
            print showtraceback(sys.exc_info(), 3)
            return

        try:
            exec code in globals()

        except SystemExit:
            self.getClientEventHandler().quit()

        except:
            print showtraceback(sys.exc_info())

    def startup(self):
        #from karmadbg.startup.firstrun import firstrun
        from karmadbg.startup.startup import startup
        #firstrun()
        startup()

    #def getAutoComplete(self, startAutoComplete):
    #    return []