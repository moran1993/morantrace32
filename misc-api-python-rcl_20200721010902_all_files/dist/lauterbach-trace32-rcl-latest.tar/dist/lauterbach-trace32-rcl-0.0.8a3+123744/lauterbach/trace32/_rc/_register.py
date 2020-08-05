import ctypes
import struct


class Register:
    """
    This is register documentation
    """
    def __init__(self, connection, *, core=None, name=None, type_=None, value=None, fvalue=None, float_mode=0):
        """
        This is Register.__init__ documentation
        """
        self.__connection = connection
        self.__core = core
        self.__name = name
        self.__type = type_
        self.__value = value
        self.__fvalue = fvalue
        self.__float_mode = float_mode

    def __str__(self):
        if self.__value:
            tempvalue = self.__value
            i = 0
            while tempvalue[i] == 0 and i < (len(tempvalue) - 1):
                i = i + 1
            tempvalue = tempvalue[i:len(tempvalue)]
        else:
            tempvalue = None

        return "{{name: '{}', type_: '{}'{value:}{fvalue:}{core:}}}".format(
            self.__name,
            self.__type,
            value='' if tempvalue is None else ', value: 0x{}'.format(''.join(format(x, '02X') for x in tempvalue)),
            fvalue='' if self.__fvalue is None else ', fvalue: {}'.format(self.__fvalue),
            core='' if self.__core is None else ', core: {}'.format(self.__core))

    def to_dict(self):
        return {'name': self.__name, 'type_': self.__type, 'core': self.__core,
                'value': self.__value, 'fvalue': self.__fvalue}

    @property
    def core(self):
        return self.__core

    @core.setter
    def core(self, core):
        self.__core = core

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if isinstance(value, bytes):
            self.__value = value
        else:
            raise TypeError
        self.__fvalue = None

    @property
    def ivalue(self):
        return int.from_bytes(self.__value, byteorder='big', signed=True)

    @ivalue.setter
    def ivalue(self, value):
        if isinstance(value, int):
            self.__value = struct.pack(">q", value)
        else:
            raise TypeError
        self.__fvalue = None

    @property
    def fvalue(self):
        return self.__fvalue

    @fvalue.setter
    def fvalue(self, fvalue):
        if isinstance(fvalue, float):
            self.__fvalue = fvalue
        else:
            raise TypeError
        self.__value = None

    def read(self):
        return self.__connection.read(name=self.name, core=self.core, unit=self.__type)

    def write(self):
        if self.__fvalue:
            self.__connection.write(self.name, self.__fvalue, core=self.core, unit=self.__type)
        else:
            self.__connection.write(self.name, self.__value, core=self.core, unit=self.__type)
        return self


class RegisterService:
    def __init__(self, intf):
        self.__intf = intf

    def __call__(self, *args, **kwargs):
        return Register(self.__intf, *args, **kwargs)

    def __extract_from_answer(self, bytestring):
        """
        generates a list of Register object from the bytestring received from the API

        Args:
            bytestring (bytes): Bytes containing the answer of the API

        Returns:
            List(Register): Result
        """
        counter = 0
        name = None
        reg_type = None
        value = None
        fvalue = None
        core = None
        registers = []
        while counter < len(bytestring):
            if bytestring[counter:(counter + 2)] == b'NM':
                # Name extraction
                name_len = int.from_bytes(bytestring[(counter + 2):(counter + 3)], byteorder='little', signed=True)
                name = (bytestring[(counter + 4):(counter + name_len + 4)]).decode('unicode_escape')
                counter += 4 + name_len

            if bytestring[counter:(counter + 2)] == b'TY':
                # Type extraction
                reg_type = (bytestring[(counter + 2):(counter + 5)]).decode('unicode_escape')
                counter += 6

            if bytestring[counter:(counter + 2)] == b'VA':
                # Value extraction
                value = bytestring[(counter + 2):(counter + 10)]
                counter += 10

            if bytestring[counter:(counter + 2)] == b'FV' and reg_type == 'FPU':
                fvalue = struct.unpack('>d', bytestring[(counter + 2):(counter + 10)])[0]
                counter += 10

            if bytestring[counter:(counter + 2)] == b'CO':
                # Core extraction
                core = int.from_bytes(bytestring[(counter + 2):(counter + 4)], byteorder='big', signed=True)
                counter += 4

            if bytestring[counter:(counter + 2)] == b'XX':
                counter += 4
                registers.append(Register(self, core=core, name=name, type_=reg_type, value=value,
                                          fvalue=fvalue))
                name = None
                reg_type = None
                value = None
                fvalue = None
                core = None
                continue
            counter += 1

        return registers

    def __read_write_exp(self, data):
        """
        Forwards specified data to the Api and returns the answer

        data (Bytes): Bytes containing the Instructions for the API

        Returns:
            Bytes: Result
        """
        return self.__extract_from_answer(self.__intf(3, data))

    @staticmethod
    def __parse_unit_to_mode(unit, mode):
        """
        parses the specified Register Type to the aquivalent API mode

        unit (String): Register Type
        mode (int): mode before mending with the bits specifying the register type

        Returns:
            int: Result
        """
        if unit is None:
            mode = mode | 0b11100
        else:
            if 'CPU' in unit.upper():
                mode = mode | 0b100
            if 'FPU' in unit.upper():
                mode = mode | 0b1000
            if 'VPU' in unit.upper():
                mode = mode | 0b10000
        return mode

    @staticmethod
    def __parse_doublemode(float_mode_string):
        """
        Returns the Api sided defined value for the specified Floating point value mode

        float_mode_string (String): floating point mode that should be used

        Returns:
            int: Result
        """
        all_float_modes = {'IEEE': 1, 'IEEE_DOUBLE': 2, 'MFFP': 3, 'IEEE_EXT_96G': 4, 'IEEE_REV': 5, 'DSP_16 ': 6,
                           'IEEE_SWAPPED': 7, 'IEEE_DOUBLE_SWAPPED': 8, 'PDP11': 9, 'PDP11_DOUBLE': 10,
                           'DSP_16_FIX': 11, 'DSP_32_FIX': 12, 'IEEE_EXT_80': 13, 'M56_DSP': 14, 'FRACT_24': 15,
                           'FRACT_48': 16, 'IEEE_DOUBLE_TOGGLE': 17, 'FRACT_16': 18, 'FRACT_32': 19, 'M560_DSP': 20,
                           'M561_DSP': 21, 'RTOSUH': 22, 'RTOSUH_DOUBLE': 23, 'DSP16_C': 24, 'FRACT_16_': 25,
                           'FRACT_32_': 26, 'LACCUM': 27, 'FRACT_64': 28, 'MICRO': 29, 'FRACT_32PLUS8': 30,
                           'FRACT_8': 31, 'UFRACT_8': 32, 'UFRACT_16': 33, 'UFRACT_24': 34, 'UFRACT_32': 35,
                           'UFRACT_48': 36, 'UFRACT_64': 37, 'MILLI': 38, 'MICRO64': 39, 'MILLI64': 40,
                           'NANO64': 41,
                           'PICO64': 42, 'IEEE_QUAD': 43, 'IEEE_EXT_96': 44, 'IEEE_HALF': 45, 'ARM_HALF': 46,
                           'BFLOAT16': 47, 'FRACT_64PLUS8': 48}
        try:
            return all_float_modes[float_mode_string]
        except KeyError:
            return 0

    @staticmethod
    def __parse_write_value(value, mode):
        """
        Parses value to bytes. The mode is adapted when we might need to parse the value to a specific float mode

        value (int): value to parse
        mode (int): mode before parsing

        Returns:
            List(int, bytes): Result
        """
        if isinstance(value, int):
            return [mode, struct.pack("q", value)]
        elif isinstance(value, float):
            return [mode | 0b100000, struct.pack("d", value)]
        elif isinstance(value, bytes):
            return [mode, struct.pack("Q", int.from_bytes(value, 'big', signed=False))]
        else:
            return [mode, struct.pack("Q", value)]

    def read(self, name, core=None, unit=None):
        """
        Reads single Register

        Args:
            name (String): Register to read.
            core (int, optional): core from which to read.
            unit (string, optional): Type that the Register should have(CPU, FPU, VPU).

        Returns:
            Register: Result
        """
        data = bytes()
        mode = self.__parse_unit_to_mode(unit, 0b10)
        data += struct.pack('2H', mode, 1)  # mode and number of registers
        name0a_len = len(name) + 1
        if name0a_len & 1:
            name0a_len += 1
        data += struct.pack('2sH{}s'.format(name0a_len), 'NM'.encode(), name0a_len, name.encode())

        if core is not None:
            data += struct.pack('2sH', 'CO'.encode(), core)

        registers = self.__read_write_exp(data=data)

        if len(registers) == 1:
            return registers[0]
        elif len(registers) == 0:
            return None
        else:
            return registers

    def read_by_names(self, names, core=None, unit=None):
        """
        Reads Registers specified by a list of names

        Args:
            names (List(String)): Names of registers to read.
            core (int, optional): core from which to read.
            unit (string, optional): Type that the Register should have(CPU, FPU, VPU).

        Returns:
            List(Register): Result
        """
        # <TEST> Jochen Code
        data = bytes()
        mode = self.__parse_unit_to_mode(unit, 0b10)
        data += struct.pack('2H', mode, len(names))  # mode and number of registers
        if core is None:
            for name in names:
                name0a_len = len(name) + 1
                if name0a_len & 1:
                    name0a_len += 1
                data += struct.pack('2sH{}s'.format(name0a_len), 'NM'.encode(), name0a_len, name.encode())
        else:
            for name in names:
                name0a_len = len(name) + 1
                if name0a_len & 1:
                    name0a_len += 1
                data += struct.pack('2sH{}s2sH'.format(name0a_len), 'NM'.encode(), name0a_len, name.encode(),
                                    'CO'.encode(), core)
        registers = self.__read_write_exp(data=data)
        if not registers:
            registers = self.__read_write_exp(data=data)
        return registers

    def read_all(self, core=None, unit=None):
        """
        Reads all accesible Registers

        Args:
            core (int, optional): core from which to read.
            unit (string, optional): Type that the Registers should have(CPU, FPU, VPU).

        Returns:
            List(Register): Result
        """
        data = bytes()
        mode = self.__parse_unit_to_mode(unit, 0)
        data += struct.pack('H', mode)
        if core is not None:
            data += struct.pack('H', core)
        else:
            data += struct.pack('H', 0xFFFF)

        # print("in register readall: data: ", data)
        registers = self.__read_write_exp(data=data)
        if not registers:
            registers = self.__read_write_exp(data=data)

        return registers

    def read_list(self, register_list, unit=None):
        """
        Reads a list of Register Objects. Might be used to update them.

        Args:
            register_list (List(Register)): Registers to read.
            unit (string, optional): Type that the Register should have(CPU, FPU, VPU).

        Returns:
            List(Register): Result
        """
        data = bytes()

        mode = self.__parse_unit_to_mode(unit, 0b10)
        data += struct.pack('2H', mode, len(register_list))
        for reg in register_list:
            name0a_len = len(reg.name) + 1
            if name0a_len & 1:
                name0a_len += 1
            data += struct.pack('2sH{}s'.format(name0a_len), 'NM'.encode(), name0a_len, reg.name.encode())
            if reg.core is not None:
                data += struct.pack('2sH', 'CO'.encode(), reg.core)
        registers = self.__read_write_exp(data=data)
        if not registers:
            registers = self.__read_write_exp(data=data)
        return registers

    def read_dict_list(self, register_dict_list, unit=None):
        """
        Reads a list of dictionaries containing Register properties generated by the to_dict function

        Args:
            register_dict_list (List(Dictionary)): Registers to read
            unit (string, optional): Type that the Register should have(CPU, FPU, VPU).

        Returns:
            List(Register): Result
        """
        register_list = []
        for reg in register_dict_list:
            register_list.append(Register(self, core=reg.get('core'), name=reg.get('name')))

        return self.read_list(register_list, unit=unit)

    def write(self, name, value, core=None, unit=None):
        """
        Writes specified value to all registers with the name name

        Args:
            name (String): Registername of register on which to write.
            value (int, float, bytes): Value to write
            core (int, optional): core on which to write.
            unit (string, optional): Type that the Register should have(CPU, FPU, VPU).

        Returns:
            Register: Result
        """
        return self.write_by_names(names=[name], core=core, unit=unit, value=value)[0]

    def write_by_names(self, names, core=None, unit=None, value=0):
        """
        Writes one specified value to all registers with a name contained in names

        Args:
            names (List(String)): Registernames of registers on which to write.
            core (int, optional): core on which to write.
            unit (string, optional): Type that the Register should have(CPU, FPU, VPU).
            value (int, float, bytes, optional): value to write

        Returns:
            List(Register): Result
        """
        data = bytes()
        mode = self.__parse_unit_to_mode(unit, 0b11)
        parse_result = self.__parse_write_value(value, mode)
        mode = parse_result[0]
        data += struct.pack('2H', mode, len(names))  # mode and number of registers
        if core is None:
            for name in names:
                name0a_len = len(name) + 1
                if name0a_len & 1:
                    name0a_len += 1
                data += struct.pack('2sH{}s2s'.format(name0a_len), 'NM'.encode(), name0a_len, name.encode(),
                                    'VA'.encode())
                data += parse_result[1]
        else:
            for name in names:
                name0a_len = len(name) + 1
                if name0a_len & 1:
                    name0a_len += 1
                data += struct.pack('2sH{}s2sH2s'.format(name0a_len), 'NM'.encode(), name0a_len, name.encode(),
                                    'CO'.encode(), core, 'VA'.encode())
                data += parse_result[1]

        registers = self.__read_write_exp(data=data)
        if not registers:
            registers = self.__read_write_exp(data=data)
        return registers
