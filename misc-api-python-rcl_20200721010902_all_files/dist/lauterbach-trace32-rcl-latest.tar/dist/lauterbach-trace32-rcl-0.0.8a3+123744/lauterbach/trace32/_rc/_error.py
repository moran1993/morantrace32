def raise_error(error_code):
    error = _error_list.get(error_code)
    if error is None:
        raise ApiError(error_code)
    else:
        raise error()


class BreakpointError(Exception):
    pass


class BreakpointAddressError(BreakpointError):
    pass


class BreakpointActionError(BreakpointError):
    pass


class ExecuteCommandError(Exception):
    pass


class ExecuteFunctionError(Exception):
    pass


class RegisterError(Exception):
    pass


class RegisterNotFoundError(RegisterError):
    pass


class ApiBaseError(Exception):
    pass


class ApiError(ApiBaseError):
    def __init__(self, error_code):
        error_details = self.__error_codes.get(error_code)
        if error_details is None:
            super().__init__('unknown error: {}'.format(error_code))
        else:
            super().__init__('{} ({}): {}'.format(error_details[0], error_code, error_details[1]))

    __error_codes = {
        0: ("T32_OK", "Ok, no error"),
        # error codes by API client
        # -1: ("T32_ERR_COM_RECEIVE_FAIL", "receiving API response failed"),
        # -2: ("T32_ERR_COM_TRANSMIT_FAIL", "sending API message failed"),
        -3: ("T32_ERR_COM_PARA_FAIL", "function parameter error"),
        -4: ("T32_ERR_COM_SEQ_FAIL", "message sequence failed"),
        -5: ("T32_ERR_NOTIFY_MAX_EVENT", "max. notify events exceeded"),
        -6: ("T32_ERR_MALLOC_FAIL", "malloc() failed"),
        # standard error codes
        2: ("T32_ERR_STD_RUNNING", "target running"),
        3: ("T32_ERR_STD_NOTRUNNING", "target not running"),
        4: ("T32_ERR_STD_RESET", "target is in reset"),
        6: ("T32_ERR_STD_ACCESSTIMEOUT", "access timeout, target running"),
        10: ("T32_ERR_STD_INVALID", "not implemented"),
        14: ("T32_ERR_STD_REGUNDEF", "registerset undefined"),
        15: ("T32_ERR_STD_VERIFY", "verify error"),
        16: ("T32_ERR_STD_BUSERROR", "bus error"),
        22: ("T32_ERR_STD_NOMEM", "no memory mapped"),
        48: ("T32_ERR_STD_RESETDETECTED", "target reset detected"),
        49: ("T32_ERR_STD_FDXBUFFER", "FDX buffer error"),
        57: ("T32_ERR_STD_RTCKTIMEOUT", "no RTCK detected"),
        60: ("T32_ERR_STD_INVALIDLICENSE", "no valid license detected"),
        64: ("T32_ERR_STD_CORENOTACTIVE", "core has no clock/power/reset in SMP"),
        67: ("T32_ERR_STD_USERSIGNAL", "user signal"),
        83: ("T32_ERR_STD_NORAPI", "tried to connect to emu"),
        113: ("T32_ERR_STD_FAILED", ""),
        123: ("T32_ERR_STD_LOCKED", "access locked"),
        128: ("T32_ERR_STD_POWERFAIL", "power fail"),
        140: ("T32_ERR_STD_DEBUGPORTFAIL", "debug port fail"),
        144: ("T32_ERR_STD_DEBUGPORTTIMEOUT", "debug port timeout"),
        147: ("T32_ERR_STD_NODEVICE", "no debug device"),
        161: ("T32_ERR_STD_RESETFAIL", "target reset fail"),
        162: ("T32_ERR_STD_EMUTIMEOUT", "emulator communication timeout"),
        164: ("T32_ERR_STD_NORTCK", "no RTCK on emulator"),
        254: ("T32_ERR_STD_ATTACH", "T32_Attach() is missing"),
        255: ("T32_ERR_STD_FATAL", "FATAL ERROR 255"),
        # function specific error codes
        90: ("T32_ERR_FN1", ""),
        91: ("T32_ERR_FN2", ""),
        92: ("T32_ERR_FN3", ""),
        93: ("T32_ERR_FN4", ""),
        0x1000: ("T32_ERR_GETRAM_INTERNAL", "T32_GetRam failed internally"),
        0x1011: ("T32_ERR_READREGBYNAME_FAILED", "T32_ReadRegisterByName: reading register failed"),
        0x1020: ("T32_ERR_WRITEREGBYNAME_NOTFOUND", "T32_WriteRegisterByName: register not found"),
        0x1021: ("T32_ERR_WRITEREGBYNAME_FAILED", "T32_WriteRegisterByName: reading register failed"),
        0x1030: ("T32_ERR_READREGOBJ_PARAFAIL", "T32_ReadRegisterObj: wrong parameters"),
        0x1031: ("T32_ERR_READREGOBJ_MAXCORE", "T32_ReadRegisterObj: max cores exceeded"),
        0x1033: ("T32_ERR_READREGSETOBJ_PARAFAIL", "T32_ReadRegisterSetObj: wrong parameters"),
        0x1034: ("T32_ERR_READREGSETOBJ_NUMREGS", "T32_ReadRegisterSetObj: number of read registers wrong"),
        0x1040: ("T32_ERR_WRITEREGOBJ_PARAFAIL", "T32_WriteRegisterObj: wrong parameters"),
        0x1041: ("T32_ERR_WRITEREGOBJ_MAXCORE", "T32_WriteRegisterObj: max cores exceeded"),
        0x1043: ("T32_ERR_WRITEREGOBJ_FAILED", "T32_WriteRegisterObj: writing register failed"),
        0x1050: ("T32_ERR_SETBP_FAILED", "T32_WriteBreakpoint/T32_WriteBreakpointObj: setting breakpoint failed"),
        0x1060: ("T32_ERR_READMEMOBJ_PARAFAIL", "T32_ReadMemoryObj: wrong parameters"),
        0x1070: ("T32_ERR_WRITEMEMOBJ_PARAFAIL", "T32_WriteMemoryObj: wrong parameters"),
        0x1071: ("T32_ERR_TRANSFERMEMOBJ_PARAFAIL", "T32_TransferMemoryBundleObj: wrong parameters"),
        0x1072: ("T32_ERR_TRANSFERMEMOBJ_TRANSFERFAIL", "T32_TransferMemoryBundleObj: transfer failed"),
        0x1080: ("T32_ERR_READVAR_ALLOC", "T32_ReadVariable*: mem alloc failed"),
        0x1081: ("T32_ERR_READVAR_ACCESS", "T32_ReadVariable*: access to symbol failed"),
        0x1091: ("T32_ERR_READBPOBJ_PARAFAIL", "T32_ReadBreakpointObj: wrong parameters"),
        0x1092: ("T32_ERR_READBPOBJ_NOTFOUND", "T32_ReadBreakpointObj: breakpoint not found"),
        0x10a1: ("T32_ERR_WRITEBPOBJ_FAILED", "T32_WriteBreakpointObj: setting BP failed"),
        0x10b0: ("T32_ERR_MMUTRANSLATION_FAIL", "T32_QueryAddressObjMmuTranslation: translation failed"),
    }


class ApiReceiveFail(ApiBaseError):
    pass


class ApiTransmitFail(ApiBaseError):
    pass


class ApiVersionError(ApiBaseError):
    pass


_error_list = {
    -1: ApiReceiveFail,
    -2: ApiTransmitFail,
    0x1010: RegisterNotFoundError,
    0x1032: RegisterNotFoundError,
    0x1042: RegisterNotFoundError,
    0x10a2: BreakpointAddressError,
    0x10a3: BreakpointActionError,
    0x10c0: ExecuteCommandError,
    0x10c1: ExecuteFunctionError
}
