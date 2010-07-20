import os

from collections import deque
from ConfigParser import SafeConfigParser
from ConfigParser import Error as ConfigParserError


class _Event(object):
    pass

class HandleFileEvent(_Event):
    def __init__(self, loader, name, path, pattern):
        self.path = path
        self.loader = loader
        self.name = name
        self.pattern = pattern


class _EventHook(object):
    def __init__(self):
        self._handlers = deque()
    
    def __call__(self, event):
        for handler in self._handlers:
            result = handler(event)
            if result:
                return result
    
    def __iadd__(self, handler):
        self._handlers.appendleft(handler)
        return self
        
    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self


class events(object):
    HandleFile = _EventHook()



CFG_NAME = 'unittest.cfg'
def loadPlugins(projectDir):
    cfgPath = os.path.join(projectDir, CFG_NAME)
    plugins = loadPluginsConfigFile(cfgPath)
    for plugin in plugins:
        __import__(plugin)

def loadPluginsConfigFile(path):
    parser = SafeConfigParser()
    parser.read(path)
    plugins = []
    try:
        return [line for line in 
                 parser.get('unittest', 'plugins').splitlines()
                 if line.strip()]
    except ConfigParserError:
        return plugins
