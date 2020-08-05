import struct


class PracticeService:
    def __init__(self, intf):
        self.__intf = intf

    def get_macro(self, name: str) -> str:
        """Get (global) PRACTICE macro.

        Args:
            name: Name of the Macro.

        Returns:
            value (str): Value of the macro.

        Todo:
            Raise PracticeMacroNotFound exception when macro name was not found?
        """
        data = struct.pack('<HH{}s'.format(len(name)), 0, len(name), name.encode())
        return self.__intf(2, data)[2:].decode()

    def set_macro(self, name: str, value: str) -> None:
        """Set (global) PRACTICE macro.

        Args:
            name: Name of the Macro.
            value: Value of the Macro

        Returns:
            None
        """
        data = struct.pack('<HH{}sH{}s'.format(len(name), len(value)), 1, len(name), name.encode(), len(value), value.encode())
        return self.__intf(2, data)
