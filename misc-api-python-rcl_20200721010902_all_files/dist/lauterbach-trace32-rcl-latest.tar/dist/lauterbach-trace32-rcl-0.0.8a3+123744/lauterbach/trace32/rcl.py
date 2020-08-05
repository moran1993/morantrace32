import collections
import ctypes
import decimal
import enum
import logging
import re
import struct
import sys
import threading
import typing
import time
import uuid


from ._rc._address import *
from ._rc._breakpoint import *
from ._rc._error import *
from ._rc._functions import *
from ._rc._library import *
from ._rc._practice import *
from ._rc._register import *
from ._rc._symbol import *


__t32sys = None
_library = None


VERSION = '0.0.8a3'
REVISION = '$Revision: 123744 $'
BUILD = REVISION[11:-2]


def hexversion():
    """The module version as a 32-bit integer.

    See also: https://docs.python.org/3/library/sys.html#sys.hexversion
    See also: https://docs.python.org/3/c-api/apiabiversion.html#apiabiversion

    Returns:
        int: The module version as a 32-bit integer.
    """
    re_version_match = re.match(r'^(?P<major_version>\d+)\.(?P<minor_version>\d+)\.(?P<micro_version>\d+)(?:(?P<release_level>a|b|rc)(?P<release_serial>\d+))?$', VERSION)
    if re_version_match.groupdict()['release_level'] is None:
        return (int(re_version_match.groupdict()['major_version']) << 24) | \
               (int(re_version_match.groupdict()['minor_version']) << 16) | \
               (int(re_version_match.groupdict()['micro_version']) << 8) | \
               (0xF << 4)
    else:
        release_level = {None: 0xF, 'a': 0xA, 'b': 0xB, 'rc': 0xC}
        return (int(re_version_match.groupdict()['major_version']) << 24) | \
               (int(re_version_match.groupdict()['minor_version']) << 16) | \
               (int(re_version_match.groupdict()['micro_version']) << 8) | \
               (release_level[re_version_match.groupdict()['release_level']] << 4) | \
               int(re_version_match.groupdict()['release_serial'])


class __TeeOut(object):
    def __init__(self, pipe, stream, encoding):
        self.stream = stream
        self.pipe = pipe
        self.encoding = encoding

    def __getattr__(self, attr_name):
        return getattr(self.stream, attr_name)

    def write(self, data):
        self.pipe.write(data.encode(self.encoding))
        self.pipe.flush()

    def flush(self):
        self.stream.flush()


class __TeeIn(object):
    def __init__(self, pipe, stream, encoding):
        self.stream = stream
        self.pipe = pipe
        self.encoding = encoding

    def __getattr__(self, attr_name):
        # print ("getattr!",attr_name)
        sys.stdout.flush()
        a = getattr(self.pipe, attr_name)
        # print(a)
        return a

    def read(self, data):
        print("Read!")
        sys.stdout.flush()
        return self.pipe.read(data)

    def readline(self):
        buf = ""  # storage buffer
        handle = self.pipe
        chunk_size = 1
        line_separator = '\r'
        while not handle.closed:  # while our handle is open
            data = handle.read(chunk_size)  # read `chunk_size` sized data from the passed handle
            sys.stdout.write(data.decode(self.encoding))
            buf += data.decode(self.encoding)  # add the collected data to the internal buffer
            if line_separator in buf:  # we've encountered a separator
                sys.stdout.write("\n")
                chunks = buf.split(line_separator)
                buf = chunks.pop()  # keep the last entry in our buffer
                for chunk in chunks:  # yield the rest
                    return chunk
        if buf:
            return buf  # return the last buffer if any

    def flush(self):
        self.con.flush()


def autoconnect():
    encoding = "ansi"
    try:
        "Hello!".encode(encoding)
    except:  # TODO PEP 8: do not use bare 'except'
        encoding = "ascii"

    pars = sys.argv[1].split(";")
    t32sys = ''  # system path
    port = 0  # port number
    input_pipe_name = ''  # '\\\\.\\pipe\\t32pipe' #  pars[2]
    output_pipe_name = ''

    for arg in pars:
        if arg.find('systempath=') == 0:
            t32sys = arg[arg.find('systempath=') + len('systempath='):]
        if arg.find('port=') == 0:
            port = arg[arg.find('port=') + len('port='):]
        if arg.find('t32topy=') == 0:
            input_pipe_name = arg[arg.find('t32topy=') + len('t32topy='):]
        if arg.find('pytot32=') == 0:
            output_pipe_name = arg[arg.find('pytot32=') + len('pytot32='):]

    del sys.argv[1]

    if input_pipe_name != "" and output_pipe_name != "":
        # print("Redirecting output to debugger window using pipes {} and  and {} encoding.".format(input_pipe_name,
        #                                                                                          output_pipe_name,
        #

        input_pipe = open(input_pipe_name, 'rb')
        output_pipe = open(output_pipe_name, 'wb')
        sys.stdin = __TeeIn(input_pipe, sys.stdin, encoding)
        sys.stdout = __TeeOut(output_pipe, sys.stdout, encoding)
        sys.stderr = __TeeOut(output_pipe, sys.stderr, encoding)

        print('To launch this script from outside T32, use following command line:')
        print('python {} systempath={};port={} <your list of parameters>'
              .format(sys.argv[0], t32sys, port))
    # else:
    #     print("No output redirection")

    init(t32sys=t32sys)
    return connect(port=port)


def init(**kwargs):
    """Initialize module.

    Args:
        t32sys (str, optional, default=None): TRACE32 system directory. Defaults to None
    """
    print('RCL version: {}+{}'.format(VERSION, BUILD))
    global __t32sys
    global _library
    if 't32sys' in kwargs:
        t32sys = kwargs['t32sys']
        _library = Library(t32sys)
        __t32sys = t32sys
    else:
        t32sys = None
        _library = Library(t32sys)
        __t32sys = t32sys


# callback_function_type = ctypes.CFUNCTYPE(ctypes.c_int)
#
#
# def callback_function(p0):
#     print('CALLBACK')


callback_function_type = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_uint64, ctypes.c_uint64)


def callback_function(p0, p1, p2):
    print('CALLBACK', p0, p1, p2)


c_callback_function = callback_function_type(callback_function)


def connect(*, node='localhost', port=20000, packlen=1024, timeout=10.0):
    """Connect to a debugger.

    Args:
        node (str): Remote API node. Defaults to 'localhost'.
        port (:obj:`int`): Remote API port. Defaults to 20000.
        packlen (:obj:`int`): Remote API packet length. Defaults to 1024.
        timeout (:obj:`float`): Connection establishment timeout in seconds. Defaults to 10.0.

    Return:
        Debugger: debugger
    """
    return Debugger(node=node, port=port, packlen=packlen, timeout=timeout)


class Debugger:
    """Connect to a debugger.

    Args:
        node (str): Remote API node. Defaults to 'localhost'.
        port (:obj:`int`): Remote API port. Defaults to 20000.
        packlen (:obj:`int`): Remote API packet length. Defaults to 1024.
        timeout (:obj:`float`): Connection establishment timeout in seconds. Defaults to 10.0.

    Attributes:
        address (AddressService): :py:attr:`AddressService<lauterbach.trace32.rcl.connect.AddressService>` for this debugger.
        breakpoint (BreakpointService): :py:attr:`BreakpointService<lauterbach.trace32.rcl.connect.BreakpointService>` for this debugger.
        cmd (CommandService): :py:attr:`CommandService<lauterbach.trace32.rcl.connect.CommandService>` for this debugger.
        fnc (FunctionService): :py:attr:`FunctionService<lauterbach.trace32.rcl.connect.FunctionService>` for this debugger.
        memory (MemoryService): :py:attr:`MemoryService<lauterbach.trace32.rcl.connect.MemoryService>` for this debugger.
        register (RegisterService): :py:attr:`RegisterService<lauterbach.trace32.rcl.connect.RegisterService>` for this debugger.
        symbol (SymbolService): :py:attr:`SymbolService<lauterbach.trace32.rcl.connect.SymbolService>` for this debugger.
        variable (VariableService): :py:attr:`VariableService<lauterbach.trace32.rcl.connect.VariableService>` for this debugger.
    """

    def __init__(self, *, node='localhost', port=20000, packlen=1024, timeout=10.0):
        global _library
        if _library is None:
            raise ValueError('"init()" required before "connect()"')
        self.__library = _library
        self.__channel = None
        self.f = GenericFunctions(self)
        channel_size = self.__library.get_handle().T32_GetChannelSize()
        channel = (ctypes.c_char * channel_size)()
        self.__library.get_handle().T32_GetChannelDefaults(ctypes.byref(channel))
        self.__library.get_handle().T32_SetChannel(ctypes.byref(channel))
        self.__library.t32_config(b"NODE=", node.encode())
        self.__library.t32_config(b"PORT=", str(port).encode())
        self.__library.t32_config(b"PACKLEN=", str(packlen).encode())
        # t32_init and t32_attach with optional timeout
        if timeout is not None:
            timeout_start = time.perf_counter()
        while True:
            self.__library.t32_init()
            self.__library.t32_exit()
            try:
                self.__library.t32_init()
                self.__library.t32_attach(1)  # 1 == T32_DEV_ICD
            except ApiReceiveFail:
                if timeout is not None:
                    print(time.perf_counter() - timeout_start)
                    if time.perf_counter() - timeout_start > timeout:
                        raise TimeoutError(time.perf_counter() - timeout_start)
                self.__library.t32_exit()
                continue
            break
        self.__channel = channel
        self.__event_service = None
        self.address = self.AddressService(self)
        self.breakpoint = self.BreakpointService(self)
        self.cmd = self.CommandService(self)
        self.fnc = self.FunctionService(self)
        self.memory = self.MemoryService(self)
        self.practice = PracticeService(self.t32_exp)
        self.register = RegisterService(self.t32_exp)
        self.symbol = self.SymbolService(self)
        self.variable = self.VariableService(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def __set_port(self, port):
        if port is None:
            self.__port = (20000,)
        if isinstance(port, int):
            self.__port = (port,)
        elif isinstance(port, typing.Sequence):
            self.__port = tuple(port)
        else:
            raise ValueError()

    def __set_t32sys(self, t32sys):
        if isinstance(t32sys, str):
            self.__t32sys = t32sys
        else:
            raise ValueError()

    def disconnect(self):
        self._set_channel()
        self.__library.t32_exit()

    @property
    def library(self):
        return self.__library

    def __cmd(self, command: str):
        """Only for internal use! Use 'cmd' without leading underscores instead!"""
        logging.debug(command)
        result = (ctypes.c_char * 4096)()
        try:
            self.__library.t32_executecommand(command.encode(), result, 4096)
        except ExecuteCommandError as e:
            raise ExecuteCommandError(result.value.decode()).with_traceback(e.__traceback__) from None

    def _cmd(self, command: str):
        """Only for internal use! Use 'cmd' without leading underscores instead!"""
        self._set_channel()
        self.__cmd(command)

    def _fnc(self, command: str):
        """Only for internal use! Use 'fnc' without leading underscores instead!"""
        self._set_channel()
        logging.debug(command)
        c_result_value = (ctypes.c_char * 4096)()
        c_result_type = ctypes.c_uint32()
        try:
            self.__library.t32_executefunction(command.encode(), c_result_value, 4096, c_result_type)
        except ExecuteFunctionError as e:
            raise ExecuteFunctionError(c_result_value.value.decode()) from e
        result_type = c_result_type.value
        result_value = c_result_value.value.decode()
        if result_type == 0x0000:  # error
            return str(result_value)
        elif result_type == 0x0001:  # bool
            if result_value == 'FALSE()':
                return False
            elif result_value == 'TRUE()':
                return True
            else:
                raise ValueError(result_value)
        elif result_type == 0x0002:  # binary
            return int(result_value[2:], 2)
        elif result_type == 0x0004:  # hex
            return int(result_value, 16)
        elif result_type == 0x0008:  # decimal
            return int(result_value[:-1])
        elif result_type == 0x0010:  # float
            return float(result_value)
        elif result_type == 0x0020:  # TODO ascii constant
            print(result_value)
            return str(result_value)
        elif result_type == 0x0040:  # string
            return str(result_value)
        elif result_type == 0x0080:  # TODO numeric range
            return str(result_value)
        elif result_type == 0x0100:  # TODO address
            return str(result_value)
        elif result_type == 0x0200:  # TODO address range
            return str(result_value)
        elif result_type == 0x0400:  # time
            return float(result_value[:-1])
        elif result_type == 0x0800:  # time range
            return [float(tv[:-1]) for tv in result_value.split('--')]
        elif result_type == 0x4000:  # TODO bitmask
            return str(result_value)
        elif result_type == 0x8000:  # empty
            return None
        return None

    def _set_channel(self):
        self.__library.get_handle().T32_SetChannel(ctypes.byref(self.__channel))

    class EventService:
        pass

    class EventPollThread(threading.Thread):
        def __init__(self, connection):
            super().__init__()
            self.__connection = connection

        def run(self):
            while True:
                self.__connection.event_poll()

    @property
    def event(self):
        if self.__event_service is None:
            self.__event_service = self.EventService(self)
        return self.__event_service

    def event_init(self):
        self._set_channel()
        # self.__library.t32_notifyeventenable(b'SYSUP', callback_function_type(callback_function))
        self.__callback = c_callback_function
        self.__library.t32_notifystateenable(0x00, c_callback_function)

    def event_init_poll(self):
        self._set_channel()
        # self.__library.t32_notifyeventenable(b'SYSUP', callback_function_type(callback_function))
        self.__callback = c_callback_function
        self.__library.t32_notifystateenable(0x00, c_callback_function)
        self.EventPollThread(self).start()

    def event_poll(self):
        self._set_channel()
        self.__library.t32_checkstatenotify(0)

    def print(self, string):
        self.cmd('ECHO "{}"'.format(string))

    def t32_ping(self):
        self._set_channel()
        self.__library.t32_ping()

    class CommandService:
        def __init__(self, parent):
            self.__parent = parent

        def __call__(self, command: str):
            self.__parent._cmd(command)

    def cmm(self, cmd: str, *, error_check: bool = False, timeout: float = 0):
        """Executes PRACTICE *.cmm script, blocking.

        Args:
            cmd (str): Script path and name.
            error_check (bool): Set to check for occurred errors.
            timeout (float, optional, default=0): Timeout in seconds.
                Special values:
                - None: Don't poll for script to finish (non-blocking)
                - 0: Wait indefinitely.

        Raises:
            TimeoutError: If script execution took longer than timeout.
            
        Todo:
            recursive check of caller until script name is different
            returned values PRACTICE.ARGS()
        """
        self._set_channel()
        if error_check:
            self.__cmd('ERROR.RESet')
        if timeout is not None:
            caller_file_pre = self.fnc('PRACTICE.CALLER.FILE(0.)')
            caller_line_pre = self._fnc('PRACTICE.CALLER.LINE(0.)')
        start_time = time.perf_counter()
        self.__cmd('DO {}'.format(cmd))
        practice_state = ctypes.c_int()
        if timeout is not None:
            while True:
                self.__library.t32_getpracticestate(practice_state)
                if practice_state.value == 0:
                    # not running
                    break
                elif practice_state.value == 1:
                    # running
                    pass
                elif practice_state.value == 2:
                    # dialog window open
                    pass
                else:
                    raise ValueError('Unknown / Invalid practice state: {}'.format(practice_state.value))
                if timeout != 0:
                    if time.perf_counter() - start_time > timeout:
                        raise TimeoutError()
            if error_check:
                print(self.cmd_eval(b'EVAL ERROR.OCCURRED()'))
            caller_file_post = self.cmd_str('PRACTICE.CALLER.FILE(0.)')
            caller_line_post = self.cmd_int('PRACTICE.CALLER.LINE(0.)')
            # print(caller_file_post)
            # print(caller_line_post)

    def cmd_bool(self, cmd: str) -> int:
        result = ctypes.c_uint32()
        self._set_channel()
        self.__cmd('EVAL {}'.format(cmd))
        self.__library.t32_evalget(result)
        if result.value == 0:
            return False
        elif result.value == 1:
            return True
        else:
            raise ValueError(result.value)

    def cmd_int(self, cmd: str) -> int:
        result = (ctypes.c_char * 4096)()
        self._set_channel()
        self.__cmd('EVAL FORMAT.Decimal(0,{})'.format(cmd))
        self.__library.t32_evalgetstring(result)
        return int(result.value)

    def cmd_float(self, cmd: str) -> float:
        result = (ctypes.c_char * 4096)()
        self._set_channel()
        self.__cmd('EVAL FORMAT.FLOAT(0,0,{})'.format(cmd))
        self.__library.t32_evalgetstring(result)
        return float(result.value)

    def cmd_decimal(self, cmd: str) -> decimal.Decimal():
        result = (ctypes.c_char * 4096)()
        self._set_channel()
        self.__cmd('EVAL FORMAT.FLOAT(0,0,{})'.format(cmd))
        self.__library.t32_evalgetstring(result)
        return decimal.Decimal(result.value.decode())

    def cmd_str(self, cmd: str) -> str:
        result = (ctypes.c_char * 4096)()
        self._set_channel()
        self.__cmd('EVAL {}'.format(cmd))
        self.__library.t32_evalgetstring(result)
        return result.value.decode()

    class FunctionService:
        def __init__(self, parent):
            self.__parent = parent

        def __call__(self, command: str):
            return self.__parent._fnc(command)

    def t32_stop(self):
        self._set_channel()
        self.__library.t32_stop()

    def t32_eval_get(self):
        evaluation_result = ctypes.c_uint32()
        self._set_channel()
        self.__library.t32_evalget(evaluation_result)
        return evaluation_result.value

    def t32_eval_get_string(self):
        evaluation_string = (ctypes.c_char * 4096)()
        self._set_channel()
        self.__library.t32_evalgetstring(evaluation_string)
        return evaluation_string.value

    def _get_practice_state(self):
        self._set_channel()
        practice_state = ctypes.c_int()
        self.__library.t32_getpracticestate(practice_state)
        return practice_state.value

    def get_window_content(self, *, command: str, requested: int, offset: int, print_code: str) -> bytes:
        PRINT_CODES = {'ASCII': 0x41, 'ASCIIP': 0x42, 'ASCIIE': 0x43, 'CSV': 0x44, 'XML': 0x45}
        try:
            print_code_int = PRINT_CODES[print_code]
        except KeyError:
            raise ValueError('Invalid print_code: "{}". Valid print_codes: "{}"'.format(print_code, '", "'.join(PRINT_CODES.keys()))) from None
        self._set_channel()
        buffer = (ctypes.c_char * requested)()
        result = self.__library.get_handle().T32_GetWindowContent(command.encode(), buffer, requested, offset, print_code_int)
        print('result = {}'.format(result))
        if result < 0:
            raise Error(None, 'T32_GetWindowContent: error')
        print(len(buffer.value))
        print(len(bytes(buffer.value)))
        return buffer.value.decode()

    def get_message(self):
        # execute
        message_text = (ctypes.c_char * 256)()
        message_type = ctypes.c_uint16()
        self._set_channel()
        self.__library.t32_getmessage(message_text, message_type)
        return collections.namedtuple('message', ['text', 'type'])(message_text.value.decode(), message_type.value)

    def step(self):
        self._set_channel()
        # self.__cmd('Step')
        self.__library.t32_step()

    def step_asm(self):
        self._set_channel()
        # self.__cmd('Step.Asm')
        self.__library.t32_stepmode(0)

    def step_hll(self):
        self._set_channel()
        # self.__cmd('Step.Hll')
        self.__library.t32_stepmode(1)

    def step_over(self):
        self._set_channel()
        self.__cmd('Step.Over')

    def go(self):
        self._set_channel()
        # self.__cmd('Go')
        self.__library.t32_go()

    def go_up(self):
        self._set_channel()
        self.__cmd('Go.Up')

    def go_return(self):
        self._set_channel()
        self.__cmd('Go.Return')

    def break_(self):
        self._set_channel()
        # self.__cmd('Break')
        self.__library.t32_break()

    def get_state(self):
        self._set_channel()
        c_state = ctypes.c_int()
        self.library.t32_getstate(ctypes.byref(c_state))
        return c_state.value

    class MemoryService:
        def __init__(self, parent):
            self.__parent = parent

        def read(self, *args, **kwargs):
            return self.__parent.memory_read(*args, **kwargs)

        def read_int8(self, address, *, width=1):
            """Read signed 8-bit value from address and return result.

            Args:
                address (Address): Address to read from.
                width (int, optional): Reserved.

            Returns:
                int: Result
            """
            buffer = self.read(address=address, length=1, width=width)
            return struct.unpack('b', buffer)[0]

        def read_int8_array(self, address, *, length, width=1):
            """Read signed 8-bit array from address and return result.

            Args:
                address (Address): Address to read from
                length (int): Array Length.
                width (int, optional): Reserved.

            Returns:
                Tuple[int]: Result
            """
            buffer = self.read(address=address, length=length, width=width)
            return struct.unpack('{}b'.format(length), buffer)

        def read_uint8(self, address: Address, *, width=1):
            """Read unsigned 8-bit value from address and return result.

            Args:
                address (Address): Address to read from
                width (int, optional): Reserved.

            Returns:
                int: Result
            """
            buffer = self.read(address=address, length=1, width=width)
            return struct.unpack('B', buffer)[0]

        def read_uint8_array(self, address, *, length=1, width=1):
            """Read unsigned 8-bit values from address and return result.

            Args:
                address (Address): Address to read from
                length (int): Number of 8-bit values to read
                width (int, optional): Reserved.

            Returns:
                Tuple[int]: Result
            """
            buffer = self.read(address=address, length=length, width=width)
            struct.unpack('{}B'.format(length), buffer)

        def read_int16(self, address, *, width=2):
            """Read unsigned 8-bit value from address and return result.

            Args:
                address [Address]: Address to read from
                width (int, optional): Reserved.

            Returns:
                Tuple[int]: Result
            """
            buffer = self.read(address=address, length=2, width=width)
            return struct.unpack('h', buffer)[0]

        def read_uint16(self, address, *, width=2):
            """Read unsigned 8-bit values from address and return result.

            Args:
                address (Address): Address to read from
                width(int): Reserved

            Returns:
                Tuple[int]: Result
            """
            buffer = self.read(address=address, length=2, width=width)
            return struct.unpack('H', buffer)[0]

        def read_int32(self, address, *, width=4):
            """Read unsigned 8-bit values from address and return result.

            Args:
                address (Address): Address to read from
                width(int): Reserved

            Returns:
                Tuple[int]: Result
            """
            buffer = self.read(address=address, length=4, width=width)
            return struct.unpack('i', buffer)[0]

        def read_uint32(self, address, *, width=4):
            """Read unsigned 8-bit values from address and return result.

            Args:
                address (Address): Address to read from
                width(int): Reserved

            Returns:
                Tuple[int]: Result
            """
            buffer = self.read(address=address, length=4, width=width)
            return struct.unpack('I', buffer)[0]

        def read_int64(self, address, *, width=8):
            """Read unsigned 8-bit values from address and return result.

            Args:
                address (Address): Address to read from
                width(int): Reserved

            Returns:
                Tuple[int]: Result
            """
            buffer = self.read(address=address, length=8, width=width)
            return struct.unpack('q', buffer)[0]

        def read_uint64(self, address, *, width=8):
            """Read unsigned 8-bit values from address and return result.

            Args:
                address (Address): Address to read from
                width(int): Reserved

            Returns:
                Tuple[int]: Result
            """
            buffer = self.read(address=address, length=8, width=width)
            return struct.unpack('Q', buffer)[0]

        def read_float(self, address, *, width=4):
            buffer = self.read(address=address, length=4, width=width)
            return struct.unpack('f', buffer)[0]

        def read_double(self, address, *, width=8):
            buffer = self.read(address=address, length=8, width=width)
            return struct.unpack('d', buffer)[0]

        def write(self, *args, **kwargs):
            return self.__parent.memory_write(*args, **kwargs)

        def write_int8(self, address, value, *, width=1):
            """Write signed 8-bit value to address.

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.
            """
            buffer = struct.pack('b', value)
            self.write(address=address, buffer=buffer, length=1, width=width)

        def write_int8_array(self, address, data, *, width=1):
            """Write data as signed 8-bit values to address.

            Args:
                address (Address): Address to read from
                data (Tuple[int]): Data to write.
                width (int, optional): Reserved.
            """
            data_len = len(data)
            buffer = struct.pack('{}b'.format(data_len), *data)
            self.write(address=address, buffer=buffer, length=data_len, width=width)

        def write_uint8(self, address, value, *, width=1):
            """Write unsigned 8-bit value to address.

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.
            """
            buffer = struct.pack('B', value)
            self.write(address=address, buffer=buffer, length=1, width=width)

        def write_uint8_array(self, address, data, *, width=1):
            """Write data as signed 8-bit values to address.

            Args:
                address (Address): Address to read from
                data (Tuple[int]): Data to write.
                width (int, optional): Reserved.
            """
            data_len = len(data)
            buffer = struct.pack('{}B'.format(data_len), *data)
            self.write(address=address, buffer=buffer, length=data_len, width=width)

        def write_int16(self, address, value, *, width=2):
            """Write signed 16-bit value to address.

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.
            """
            buffer = struct.pack('h', value)
            self.write(address=address, buffer=buffer, length=2, width=width)

        def write_uint16(self, address, value, *, width=2):
            """Write unsigned 16-bit value to address.

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.
            """
            buffer = struct.pack('H', value)
            self.write(address=address, buffer=buffer, length=2, width=width)

        def write_int32(self, address, value, *, width=4):
            """Write signed 32-bit value to address.

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.
            """
            buffer = struct.pack('i', value)
            self.write(address=address, buffer=buffer, length=4, width=width)

        def write_uint32(self, address, value, *, width=4):
            """Write unsigned 32-bit value to address.

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.
            """
            buffer = struct.pack('I', value)
            self.write(address=address, buffer=buffer, length=4, width=width)

        def write_int64(self, address, value, *, width=8):
            """Write signed 64-bit value to address.

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.
            """
            buffer = struct.pack('q', value)
            self.write(address=address, buffer=buffer, length=8, width=width)

        def write_uint64(self, address, value, *, width=8):
            """Write unsigned 64-bit value to address.

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.
            """
            buffer = struct.pack('Q', value)
            self.write(address=address, buffer=buffer, length=8, width=width)

        def write_float(self, address, value, *, width=4):
            buffer = struct.pack('f', value)
            self.write(address=address, buffer=buffer, length=4, width=width)

        def write_double(self, address, value, *, width=8):
            buffer = struct.pack('d', value)
            self.write(address=address, buffer=buffer, length=8, width=width)

    def memory_read(self, *, address: Address, length: int, width=1):
        self._set_channel()
        # request
        bufferobj_handle = ctypes.c_void_p()
        self.__library.t32_requestbufferobj(bufferobj_handle, length)
        c_address = CAddress(self.__library).from_address(address)
        # execute
        self.__library.t32_readmemoryobj(bufferobj_handle, c_address.obj, length)
        cbuffer = (ctypes.c_uint8 * length)()
        self.__library.t32_copydatafrombufferobj(cbuffer, length, bufferobj_handle)
        # release
        self.__library.t32_releasebufferobj(bufferobj_handle)
        # return
        return bytes(cbuffer)

    def memory_write(self, *, address: Address, buffer, length, width=1):
        # request
        bufferobj_handle = ctypes.c_void_p()
        self.__library.t32_requestbufferobj(bufferobj_handle, length)
        if type(address) == str:
            addr_match = re_addr.match(address)
            address = Address(self, **addr_match.groupdict())
        c_address = CAddress(self.__library).from_address(address)
        # set
        cbuffer = (ctypes.c_uint8 * length)(*buffer)
        self.__library.t32_copydatatobufferobj(bufferobj_handle, length, cbuffer)
        # execute
        self._set_channel()
        self.__library.t32_writememoryobj(bufferobj_handle, c_address.obj, length)
        # release
        self.__library.t32_releasebufferobj(bufferobj_handle)

    class AddressService:
        def __init__(self, parent):
            self.__parent = parent

        def __call__(self, *args, **kwargs):
            return Address(self.__parent, *args, **kwargs)

        def from_string(self, string):
            return Address.from_string(self.__parent, string)

    class BreakpointService:
        def __init__(self, parent):
            self.__parent = parent

        def __call__(self, *args, **kwargs):
            return Breakpoint(self.__parent, *args, **kwargs)

        def set(self, *args, **kwargs):
            """Set breakpoint

            Args:
                address (Address): Address to write to.
                value (int): Value to write.
                width (int, optional): Reserved.

            Returns:
            """
            return Breakpoint(self.__parent, *args, **kwargs).set()

        def list(self):
            """

            """
            return self.__parent._breakpoint_list()

    def _breakpoint_delete(self, bp):
        self._set_channel()
        c_bp = CBreakpoint.from_breakpoint(bp, self.library)
        c_bp.write()

    def _breakpoint_list(self):
        self._set_channel()
        c_bp_count = ctypes.c_uint32()
        self.__library.t32_querybreakpointobjcount(c_bp_count)
        bp_count = c_bp_count.value
        bps = []
        for bp_i in range(bp_count):
            c_bp = CBreakpoint(self.__library).read_by_index(bp_i)
            bp = c_bp.to_breakpoint(self)
            bps.append(bp)
        return bps

    def _breakpoint_set(self, bp):
        self._set_channel()
        c_bp = CBreakpoint.from_breakpoint(bp, self.library)
        c_bp.write()

    class SymbolService:
        def __init__(self, parent):
            self.__parent = parent

        def __call__(self, *args, **kwargs):
            return Symbol(self.__parent, *args, **kwargs)

        def query_by_address(self, address):
            """Search symbol by address.

            Args:
                Address (Address): Name with which the symbol is searched.

            Returns:
                Symbol: Result
            """
            return self.__parent._symbol_query(address=address)

        def query_by_name(self, name):
            """Search symbol by name.

            Args:
                name (str): Address at which the symbol is searched.

            Returns:
                Symbol: Result
            """
            return self.__parent._symbol_query(name=name)

    def _symbol_query(self, *, address=None, name=None):
        if address is None and name is None:
            raise ValueError('Either address or name must be set to query, but not both.')
        elif address is not None and name is not None:
            raise ValueError('Either address or name must be set to query, but not both.')
        c_sym = CSymbol(self.__library)
        if name is not None:
            c_sym.name = name
        elif address is not None:
            c_sym.address = address
        self._set_channel()
        self.__library.t32_querysymbolobj(c_sym.obj)
        if c_sym.size == 0xFFFFFFFFFFFFFFFF:
            # TODO Improve Remote API to enable better check if no symbol is found
            return None
        else:
            return c_sym.to_symbol(self)

    class VariableService:
        def __init__(self, parent):
            self.__parent = parent

        def read(self, *args, **kwargs):
            return self.__parent.variable_read(*args, **kwargs)

    def variable_read(self, *, name):
        self._set_channel()
        sym = self.symbol_query(name=name)
        if sym is None:
            return None
        # symbol query does not support type yet, so we have to use a workaround
        sym_type = self._fnc('Var.TYPEOF({})'.format(name))
        mem = self.memory_read(address=sym.address, length=sym.size)
        if sym_type.startswith('short int'):
            return struct.unpack('{}h'.format(sym.size // 2), mem)
        elif sym_type.startswith('int'):
            return struct.unpack('{}i'.format(sym.size // 4), mem)
        else:
            return mem

    def _read_variable_value(self, variable_name):
        variable_value_ls32bit = ctypes.c_uint32()
        variable_value_ms32bit = ctypes.c_uint32()
        self._set_channel()
        self.__library.t32_readvariablevalue(variable_name.encode(), variable_value_ls32bit, variable_value_ms32bit)
        return (variable_value_ms32bit.value << 32) | variable_value_ls32bit.value

    # def write_variable(self, variable_name):
    #     TODO this doesn't work yet
    #     """
    #     Write a variable value
    #     TODO only works for int and similar types, not for float/double/string/...
    #     :param variable:
    #     :return:
    #     """
    #     variable_value_ls32bit = ctypes.c_uint32((variable.get_value() >> 0) & 0xffffffff)
    #     variable_value_ms32bit = ctypes.c_uint32((variable.get_value() >> 32) & 0xffffffff)
    #     self._set_channel()
    #     self.__library.t32_writevariablevalue(variable.get_name(), variable_value_ls32bit, variable_value_ms32bit)

    def _read_variable_string(self, variable_name):
        c_value_size = 100
        c_value = (ctypes.c_char * c_value_size)()
        self._set_channel()
        self.__library.t32_readvariablestring(variable_name.encode(), c_value, c_value_size)
        return c_value.value

    # def window_open(self, window: Window):
    #     """
    #     see Window.open()
    #     """
    #     return window.open(self)
    #
    # def window_close(self, window: Window):
    #     """
    #     see Window.close()
    #     """
    #     return window.close(self)
    #
    # def window_query(self, window: Window):
    #     """
    #     see Window.query()
    #     """
    #     return window.query(self)
    #
    # def window_update(self, window: Window):
    #     """
    #     see Window.update()
    #     """
    #     return window.update(self)

    def t32_exp(self, cmd, data):
        T32_MAX_LINE_LEN = 16641
        self._set_channel()
        c_out_buf = (ctypes.c_char * T32_MAX_LINE_LEN)()
        c_out_len = ctypes.c_uint16()
        buffer = struct.pack('H', cmd) + data
        self.__library.t32_exp(buffer, len(buffer), c_out_buf, c_out_len)
        return bytes(c_out_buf)[2:c_out_len.value]


class WindowError(Exception):
    def __init__(self, error_message):
        super().__init__(error_message)


class Window:
    """
    Helper class for opening, position, sizing, closing, ... TRACE32 windows.
    
    TODO WinPage support
    """

    def __init__(self, window, *, left: decimal.Decimal = None, up: decimal.Decimal = None, hsize: int = None,
                 vsize: int = None, hscale: int = None, vscale: int = None, name=None, state=None, header=None):
        """
        Creates a window object.
        
        :param window: Window, e.g. "Data.dump /SpotLight"
        :param left: x-coordinate
        :param up: y-coordinate
        :param hsize: width
        :param vsize: height
        :param hscale: width of the scale area
        :param vscale: height of the scale area
        :param name: user-defined identifier for the window
        :param state: TODO not implemented
        :param header: TODO not implemented
        """
        self.__window = window
        self.__left = left      # TODO convert to decimal.Decimal?
        self.__up = up          # TODO convert to decimal.Decimal?
        self.__hsize = hsize
        self.__vsize = vsize
        self.__hscale = hscale
        self.__vscale = vscale
        self.__name = name if name is not None else uuid.uuid4()
        if state is not None:
            raise NotImplementedError('parameter "state" is not yet implemented')
        if header is not None:
            raise NotImplementedError('parameter "header" is not yet implemented')

    @staticmethod
    def __int_to_str(value: typing.Union[None, int, str]) -> str:
        """
        Converts int values to a TRACE32 compatible str (leading dot). None is converted to '', str arguments are returned unchanged.
        
        :param value: 
        :return: 
        """
        return '' if value is None else value if isinstance(value, str) else '{}.'.format(value)

    @staticmethod
    def __decimal_to_str(value: typing.Union[None, decimal.Decimal, str]) -> str:
        """
        Converts decimal.Decimal values to a TRACE32 compatible str (leading dot). None is converted to '', str arguments are returned unchanged.
        
        :param value: 
        :return: 
        """
        return '' if value is None else value if isinstance(value, str) else '{:f}'.format(value)

    def __exists(self, connection):
        """
        Checks whether a window with the same name already exists.
        
        :param connection: 
        :return: 
        """
        return False if connection.cmd_eval('WINdow.EXIST({})'.format(self.__name)) == 0 else True

    def open(self, connection):
        """
        Opens the window (window-name == uuid).
        
        Before opening the window checks whether a window with the same window-name already exists, and if yes raises a WindowError.
        :param connection: 
        :return: 
        """
        if self.__exists(connection) is True:
            raise WindowError('{} already exists'.format(self.__name))
        connection.cmd('WinPOS {left},{up},{hsize},{vsize},{hscale},{vscale},{name}'.format(
            left=self.__decimal_to_str(self.__left), up=self.__decimal_to_str(self.__up),
            hsize=self.__int_to_str(self.__hsize), vsize=self.__int_to_str(self.__vsize),
            hscale=self.__int_to_str(self.__hscale), vscale=self.__int_to_str(self.__vscale), name=self.__name))
        connection.cmd('{}'.format(self.__window))

    def close(self, connection):
        """
        Closes the window (window-name == uuid).
        
        Before closing the window checks whether a window with the same window-name exists, and if no raises a WindowError.
        :param connection: 
        :return: 
        """
        if self.__exists(connection) is False:
            raise WindowError('{} not found'.format(self.__name))
        connection.cmd('WinCLEAR {}'.format(uid=self.__name))

    def query(self, connection):
        """
        Queries the window parameter.
        
        Before querying the window checks whether a window with the same window-name exists, and if no raises a WindowError.
        :param connection: 
        :return: 
        """
        if self.__exists(connection) is False:
            raise WindowError('{} not found'.format(self.__name))
        self.__left = connection.cmd_decimal('WINdow.POSition({},LEFT)'.format(self.__name))
        self.__up = connection.cmd_decimal('WINdow.POSition({},UP)'.format(self.__name))
        self.__hsize = int(connection.cmd_decimal('WINdow.POSition({},HSIZE)'.format(self.__name)))
        self.__vsize = int(connection.cmd_decimal('WINdow.POSition({},VSIZE)'.format(self.__name)))
        self.__hscale = int(connection.cmd_decimal('WINdow.POSition({},HSCALE)'.format(self.__name)))
        self.__vscale = int(connection.cmd_decimal('WINdow.POSition({},VSCALE)'.format(self.__name)))

    def update(self, connection):
        """
        Updates the window parameter (only size at the moment).
        
        Before updating the window checks whether a window with the same window-name exists, and if no raises a WindowError.
        :param connection: 
        :return: 
        """
        if self.__exists(connection) is False:
            raise WindowError('{} not found'.format(self.__name))
        if self.__hsize is not None and self.__vsize is not None:
            connection.cmd('WinRESIZE {hsize},{vsize},{name}'.format(hsize=self.__int_to_str(self.__hsize), vsize=self.__int_to_str(self.__vsize), name=self.__name))

    @property
    def height(self):
        return self.__vsize

    @height.setter
    def height(self, value):
        self.__vsize = value

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.__hsize = value


if __name__ == '__main__':
    pass
