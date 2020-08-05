import ctypes
import enum


from ._address import *


class Breakpoint:
    def __init__(self, connection, *, action=None, address=None, type=None, impl=None, enabled=True, **kwargs):
        self.__connection = connection
        self.__action = action
        self.__address = address
        self.__enabled = enabled
        self.__impl = impl
        self.__type = type

    def __str__(self):
        return '{{address: {}, type: {}, impl: {}, action: {}, enabled: {}}}'.format(
            str(self.__address),
            'None' if self.__type is None else self.__type.name,
            'None' if self.__impl is None else self.__impl.name,
            'None' if self.__action is None else self.__action.name,
            'True' if self.__enabled else 'False')

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, action):
        self.__action = action

    @property
    def address(self):
        """The breakpoint's address.

        :getter: Returns this symbols name.
        :setter: Sets this symbol's name.
        :type: string
        """
        return self.__address

    @address.setter
    def address(self, address):
        self.__address = address

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, enabled):
        self.__enabled = enabled

    @property
    def impl(self):
        return self.__impl

    @impl.setter
    def impl(self, impl):
        self.__impl = impl

    @property
    def type(self):
        return self.__type

    @type.setter
    def type_(self, type):
        self.__type = type

    class Action(enum.IntEnum):  # enum.IntFlag in 3.6
        NONE    = 0x00
        STOP    = 0x01
        SPOT    = 0x02
        ALPHA   = 0x04
        BETA    = 0x08
        CHARLIE = 0x10
        DELTA   = 0x20
        ECHO    = 0x40

    class Type(enum.IntEnum):
        PROGRAM = 0x01
        READ = 0x02
        WRITE = 0x04
        RW = 0x06

    class Impl(enum.IntEnum):  # enum.IntFlag in 3.6
        AUTO = 0x00
        SOFT = 0x01
        ONCHIP = 0x02
        HARD = 0x04
        MARK = 0x08

    def delete(self):
        """Delete Breakpoint.

        """
        self.__connection._set_channel()
        c_bp = CBreakpoint(self.__connection.library).from_breakpoint(self, self.__connection.library)
        c_bp.delete()

    def disable(self):
        """Disable breakpoint.

        """
        self.__connection._set_channel()
        self.__enabled = False
        c_bp = CBreakpoint.from_breakpoint(self, self.__connection.library)
        c_bp.write()

    def enable(self):
        """Enable breakpoint.

        """
        self.__enabled = True
        c_bp = CBreakpoint.from_breakpoint(self, self.__connection.library)
        c_bp.write()

    def set(self):
        """Set Breakpoint.

        """
        self.__connection._set_channel()
        c_bp = CBreakpoint.from_breakpoint(self, self.__connection.library)
        c_bp.write()
        return self


class CBreakpoint:
    def __init__(self, library):
        self.__library = library
        self.__obj = ctypes.c_void_p()
        self.__library.t32_requestbreakpointobj(self.__obj)

    def __del__(self):
        self.__library.t32_releasebreakpointobj(self.__obj)

    @property
    def action(self):
        c_action = ctypes.c_uint32()
        self.__library.t32_getbreakpointobjaction(self.__obj, c_action)
        return c_action.value

    @action.setter
    def action(self, action):
        self.__library.t32_setbreakpointobjaction(self.__obj, action)

    @property
    def address(self):
        c_addr = CAddress(self.__library)
        self.__library.t32_getbreakpointobjaddress(self.__obj, c_addr.obj)
        return c_addr

    @address.setter
    def address(self, addr):
        c_addr = CAddress(self.__library).from_address(addr)
        self.__library.t32_setbreakpointobjaddress(self.__obj, c_addr.obj)

    @property
    def enabled(self):
        c_enable = ctypes.c_uint8()
        self.__library.t32_getbreakpointobjenable(self.__obj, c_enable)
        return c_enable.value

    @enabled.setter
    def enabled(self, enabled):
        self.__library.t32_setbreakpointobjenable(self.__obj, enabled)

    @property
    def impl(self):
        c_impl = ctypes.c_uint32()
        self.__library.t32_getbreakpointobjimpl(self.__obj, c_impl)
        return c_impl.value

    @impl.setter
    def impl(self, impl):
        self.__library.t32_setbreakpointobjimpl(self.__obj, impl)

    @property
    def type(self):
        c_type = ctypes.c_uint32()
        self.__library.t32_getbreakpointobjtype(self.__obj, c_type)
        return c_type.value

    @type.setter
    def type(self, type_):
        self.__library.t32_setbreakpointobjtype(self.__obj, type_)

    def read_by_index(self, index):
        self.__library.t32_readbreakpointobjbyindex(self.__obj, index)
        return self

    @staticmethod
    def from_breakpoint(bp, library):
        c_bp = CBreakpoint(library)
        if bp.action is not None:
            c_bp.action = bp.action
        if bp.address is not None:
            c_bp.address = bp.address
        if bp.enabled is not None:
            c_bp.enabled = bp.enabled
        if bp.impl is not None:
            c_bp.impl = bp.impl
        if bp.type is not None:
            c_bp.type = bp.type
        return c_bp

    def to_breakpoint(self, connection):
        bp = Breakpoint(connection)
        bp.action = Breakpoint.Action(self.action)
        bp.address = self.address
        bp.enabled = self.enabled
        bp.type_ = Breakpoint.Type(self.type)
        bp.impl = Breakpoint.Impl(self.impl)
        # TODO bp.size = self.size
        return bp

    def delete(self):
        self.__library.t32_writebreakpointobj(self.__obj, 0)

    def write(self):
        self.__library.t32_writebreakpointobj(self.__obj, 1)
