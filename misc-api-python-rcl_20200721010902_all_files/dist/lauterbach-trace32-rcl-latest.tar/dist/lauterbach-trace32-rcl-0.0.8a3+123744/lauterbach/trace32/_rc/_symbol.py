import ctypes


from ._address import *
# from . import _connection


class Symbol:
    def __init__(self, connection, *, address=None, name=None):
        self.__connection = connection
        self.__address = address
        self.__name = name
        self.__path = None
        self.__size = None

    def __del__(self):
        pass

    def __str__(self):
        return '{}{} {} {}'.format(
            self.__path if self.__path is not None else '',
            self.__name,
            str(self.address),
            self.size
        )

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, value):
        if type(value) == Address:
            self.__address = value
        else:
            raise TypeError(type(value))

    @property
    def name(self):
        """The name of the symbol.

        :getter: Returns this symbols name.
        :setter: Sets this symbol's name.
        :type: string
        """
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value):
        self.__size = value


class CSymbol:
    def __init__(self, library):
        self.__library = library
        self.__obj = ctypes.c_void_p()
        self.__library.t32_requestsymbolobj(self.__obj)

    def __del__(self):
        self.__library.t32_releasesymbolobj(self.__obj)

    @property
    def address(self):
        c_addr = CAddress(self.__library)
        self.__library.t32_getsymbolobjaddress(self.__obj, c_addr.obj)
        return c_addr

    @address.setter
    def address(self, address):
        c_addr = CAddress(self.__library).from_address(address)
        self.__library.t32_setsymbolobjaddress(self.__obj, c_addr.obj)

    @property
    def name(self):
        c_name = ctypes.c_char_p()
        self.__library.t32_getsymbolobjnameptr(self.__obj, ctypes.byref(c_name))
        if c_name.value is None:
            return None
        else:
            return c_name.value.decode()

    @name.setter
    def name(self, name):
        self.__library.t32_setsymbolobjname(self.__obj, name.encode())

    @property
    def path(self):
        c_path = ctypes.c_char_p()
        self.__library.t32_getsymbolobjpathptr(self.__obj, ctypes.byref(c_path))
        if c_path.value is None:
            return None
        else:
            return c_path.value.decode()

    @path.setter
    def path(self, path):
        self.__library.t32_setsymbolobjpath(self.__obj, path.encode())

    @property
    def size(self):
        c_size = ctypes.c_uint64()
        self.__library.t32_getsymbolobjsize(self.__obj, ctypes.byref(c_size))
        return c_size.value

    @property
    def obj(self):
        return self.__obj

    def to_symbol(self, connection):
        sym = Symbol(connection)
        sym.address = self.address.to_address(connection)
        sym.name = self.name
        sym.path = self.path
        sym.size = self.size
        return sym

    def query(self):
        connection = self.__connection
        if self.__address is None and self.__name is None:
            raise ValueError('Either address or name must be set to query, but not both.')
        elif self.__address is not None and self.__name is not None:
            raise ValueError('Either address or name must be set to query, but not both.')
        elif self.__address is not None:
            library = self.__connection.library
            if library is None:
                raise ValueError()  # TODO better error and error message
            try:
                connection._set_channel()
                c_symbol = ctypes.c_void_p()
                library.t32_requestsymbolobj(c_symbol)
                c_address = c_address_obj(library, self.__address)
                # # TODO move this part to Address class?
                # c_address = ctypes.c_void_p()
                # library.t32_requestaddressobj(c_address)
                # library.t32_setaddressobjaccessstring(c_address, self.__address.access.encode())
                # library.t32_setaddressobjaddr64(c_address, self.__address.value)
                # # TODO until here
                library.t32_setsymbolobjaddress(c_symbol, c_address)
                library.t32_querysymbolobj(c_symbol)
                self.name = self._csymbol_get_name(library, c_symbol)
            finally:
                library.t32_releasesymbolobj(c_symbol)
        else:  # if self.__address is None:
            library = connection.library
            if library is None:
                raise ValueError()  # TODO better error and error message
            try:
                connection._set_channel()
                c_symbol = ctypes.c_void_p()
                library.t32_requestsymbolobj(c_symbol)
                library.t32_setsymbolobjname(c_symbol, self.__name.encode())
                library.t32_querysymbolobj(c_symbol)
                c_address = CAddress(library)
                library.t32_getsymbolobjaddress(c_symbol, c_address.obj)
                self.__address = c_address.to_address()
            finally:
                library.t32_releasesymbolobj(c_symbol)

# end-of-file

