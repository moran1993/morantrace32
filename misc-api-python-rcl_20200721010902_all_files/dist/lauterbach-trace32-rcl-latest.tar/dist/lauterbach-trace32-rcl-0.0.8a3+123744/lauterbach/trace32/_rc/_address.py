import ctypes
import re


re_addr_access = '(?:(?P<access>.+):)?'
re_addr_machine_id = '(?:(?P<machine_id>.+):::)?'
re_addr_space_id = '(?:(?P<space_id>.+)::)?'
re_addr_value = '(?P<value>(?:[0-9]+)|(?:0x[0-9a-fA-F]+))'
re_addr = re.compile(r'^{}{}{}{}$'.format(re_addr_access, re_addr_machine_id, re_addr_space_id, re_addr_value))


class Address:
    def __init__(self, connection, *, access: str = None, value: int = None, **kwargs):
        self.__connection = connection
        self.__access = access
        if value is None:
            self.__value = None
        else:
            if type(value) == int:
                self.__value = value
            elif type(value) == str:
                self.__value = int(value, 0)
            else:
                raise TypeError(value)
        # machine_id is not yet supported
        # space_id is not yet supported

    def __str__(self):
        return '{}0x{:08x}'.format(
            '' if self.__access is None else self.__access + ':',
            self.__value)

    @property
    def access(self):
        return self.__access

    @access.setter
    def access(self, access):
        self.__access = access

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @staticmethod
    def from_string(connection, string):
        addr_match = re_addr.match(string)
        addr = Address(connection)
        addr.access = addr_match.group('access')
        addr.value = int(addr_match.group('value'), 0)
        return addr

    def to_dualport(self):
        addr_str = self.__connection.fnc('CONVert.ADDRESSTODUALPORT({})'.format(str(self)))
        return self.from_string(self.__connection, addr_str)


class CAddress:
    def __init__(self, library):
        self.__library = library
        self.__obj = ctypes.c_void_p()
        self.__library.t32_requestaddressobj(self.__obj)

    def __str__(self):
        return '{}0x{:08x}'.format(
            '' if self.access is None else self.access + ':',
            self.value)

    def __del__(self):
        self.__library.t32_releaseaddressobj(self.__obj)

    @property
    def obj(self):
        return self.__obj

    @property
    def access(self):
        c_access = (ctypes.c_char * 16)()
        self.__library.t32_getaddressobjaccessstring(self.__obj, c_access, 16)
        return c_access.value.decode()

    @access.setter
    def access(self, access):
        self.__library.t32_setaddressobjaccessstring(self.__obj, access.encode())

    @property
    def value(self):
        c_value = ctypes.c_uint64()
        self.__library.t32_getaddressobjaddr64(self.__obj, c_value)
        return c_value.value

    @value.setter
    def value(self, value):
        self.__library.t32_setaddressobjaddr64(self.__obj, value)

    def from_address(self, addr):
        self.access = '' if addr.access is None else addr.access
        self.value = addr.value
        return self

    def to_address(self, connection):
        addr = Address(connection)
        addr.access = self.access
        addr.value = self.value
        return addr
