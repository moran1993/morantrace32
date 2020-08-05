import ctypes
import os
import platform

from ._error import *


_API_VERSION_MIN = 123148


def decorator_error(function_to_decorate):
    """A decorator function to call error_handler around a function"""
    def error_handler(*args, **kwargs):
        error_code = function_to_decorate(*args, **kwargs)
        if error_code != 0:
            raise_error(error_code)
    return error_handler


class Library:
    def __init__(self, t32sys):
        self.__library_handle = None

        library_name = self.auto_detect_library_name()
        if t32sys is None:
            t32sys = os.environ.get('T32SYS')
        if t32sys is None:
            self.__library_handle = ctypes.CDLL(library_name)
        else:
            library_fullname = os.path.join(t32sys, 'demo', 'api', 'capi', 'dll', library_name)
            print('API library: "{}"'.format(library_fullname))
            self.__library_handle = ctypes.CDLL(library_fullname)

        # check api version
        self.__check_api_version()
        # TODO check TRACE32 version

        self.__library_handle.T32_Config.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.__library_handle.T32_Config.restype = ctypes.c_int

        self.__library_handle.T32_Init.argtypes = None
        self.__library_handle.T32_Init.restype = ctypes.c_int

        self.__library_handle.T32_Attach.argtypes = [ctypes.c_int]
        self.__library_handle.T32_Attach.restype = ctypes.c_int

        self.__library_handle.T32_Terminate.argtypes = [ctypes.c_int]
        self.__library_handle.T32_Terminate.restype = ctypes.c_int

        self.__library_handle.T32_Exit.argtypes = None
        self.__library_handle.T32_Exit.restype = ctypes.c_int

        self.__library_handle.T32_Ping.argtypes = None
        self.__library_handle.T32_Ping.restype = ctypes.c_int

        self.__library_handle.T32_Nop.argtypes = None
        self.__library_handle.T32_Nop.restype = ctypes.c_int

        self.__library_handle.T32_NopEx.argtypes = [ctypes.c_int, ctypes.c_int]
        self.__library_handle.T32_NopEx.restype = ctypes.c_int

        self.__library_handle.T32_NopFail.argtypes = None
        self.__library_handle.T32_NopFail.restype = ctypes.c_int

        self.__library_handle.T32_Cmd.argtypes = [ctypes.c_char_p]
        self.__library_handle.T32_Cmd.restype = ctypes.c_int

        self.__library_handle.T32_ExecuteCommand.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32]
        self.__library_handle.T32_ExecuteCommand.restype = ctypes.c_int

        self.__library_handle.T32_ExecuteFunction.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_ExecuteFunction.restype = ctypes.c_int

        self.__library_handle.T32_Stop.argtypes = None
        self.__library_handle.T32_Stop.restype = ctypes.c_int

        self.__library_handle.T32_GetPracticeState.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.__library_handle.T32_GetPracticeState.restype = ctypes.c_int

        self.__library_handle.T32_EvalGet.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_EvalGet.restype = ctypes.c_int

        self.__library_handle.T32_EvalGetString.argtypes = [ctypes.c_char_p]
        self.__library_handle.T32_EvalGetString.restype = ctypes.c_int

        self.__library_handle.T32_GetMessage.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint16)]
        self.__library_handle.T32_GetMessage.restype = ctypes.c_int

        self.__library_handle.T32_GetTriggerMessage.argtypes = [ctypes.c_char_p]
        self.__library_handle.T32_GetTriggerMessage.restype = ctypes.c_int

        self.__library_handle.T32_GetChannelSize.argtypes = None
        self.__library_handle.T32_GetChannelSize.restype = ctypes.c_int

        self.__library_handle.T32_GetChannelDefaults.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_GetChannelDefaults.restype = None

        self.__library_handle.T32_SetChannel.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_SetChannel.restype = None

        self.__library_handle.T32_APILock.argtypes = [ctypes.c_int]
        self.__library_handle.T32_APILock.restype = ctypes.c_int

        self.__library_handle.T32_APIUnlock.argtypes = None
        self.__library_handle.T32_APIUnlock.restype = ctypes.c_int

        self.__library_handle.T32_GetSocketHandle.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.__library_handle.T32_GetSocketHandle.restype = None

        self.__library_handle.T32_Go.argtypes = None
        self.__library_handle.T32_Go.restype = ctypes.c_int

        self.__library_handle.T32_Break.argtypes = None
        self.__library_handle.T32_Break.restype = ctypes.c_int

        self.__library_handle.T32_Step.argtypes = None
        self.__library_handle.T32_Step.restype = ctypes.c_int

        self.__library_handle.T32_StepMode.argtypes = [ctypes.c_int]
        self.__library_handle.T32_StepMode.restype = ctypes.c_int

        self.__library_handle.T32_ResetCPU.argtypes = None
        self.__library_handle.T32_ResetCPU.restype = ctypes.c_int

        self.__library_handle.T32_SetMode.argtypes = [ctypes.c_int]
        self.__library_handle.T32_SetMode.restype = ctypes.c_int

        self.__library_handle.T32_GetCpuInfo.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16)]
        self.__library_handle.T32_GetCpuInfo.restype = ctypes.c_int

        self.__library_handle.T32_GetState.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.__library_handle.T32_GetState.restype = ctypes.c_int

        self.__library_handle.T32_ReadMemory.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int]
        self.__library_handle.T32_ReadMemory.restype = ctypes.c_int

        self.__library_handle.T32_WriteMemory.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int]
        self.__library_handle.T32_WriteMemory.restype = ctypes.c_int

        self.__library_handle.T32_WriteMemoryPipe.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int]
        self.__library_handle.T32_WriteMemoryPipe.restype = ctypes.c_int

        self.__library_handle.T32_ReadMemoryEx.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int]
        self.__library_handle.T32_ReadMemoryEx.restype = ctypes.c_int

        self.__library_handle.T32_WriteMemoryEx.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int]
        self.__library_handle.T32_WriteMemoryEx.restype = ctypes.c_int

        self.__library_handle.T32_SetMemoryAccessClass.argtypes = [ctypes.c_char_p]
        self.__library_handle.T32_SetMemoryAccessClass.restype = ctypes.c_int

        self.__library_handle.T32_GetRam.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint16)]
        self.__library_handle.T32_GetRam.restype = ctypes.c_int

        self.__library_handle.T32_GetSource.argtypes = [ctypes.c_uint32, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetSource.restype = ctypes.c_int

        self.__library_handle.T32_GetSelectedSource.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetSelectedSource.restype = ctypes.c_int

        self.__library_handle.T32_GetSymbol.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetSymbol.restype = ctypes.c_int

        self.__library_handle.T32_GetSymbolFromAddress.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_int]
        self.__library_handle.T32_GetSymbolFromAddress.restype = ctypes.c_int

        self.__library_handle.T32_ReadVariableString.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        self.__library_handle.T32_ReadVariableString.restype = ctypes.c_int

        self.__library_handle.T32_ReadVariableValue.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_ReadVariableValue.restype = ctypes.c_int

        self.__library_handle.T32_WriteVariableValue.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32]
        self.__library_handle.T32_WriteVariableValue.restype = ctypes.c_int

        self.__library_handle.T32_GetWindowContent.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        self.__library_handle.T32_GetWindowContent.restype = ctypes.c_int

        self.__library_handle.T32_ReadRegisterByName.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_ReadRegisterByName.restype = ctypes.c_int

        self.__library_handle.T32_WriteRegisterByName.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32]
        self.__library_handle.T32_WriteRegisterByName.restype = ctypes.c_int

        self.__library_handle.T32_ReadPP.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_ReadPP.restype = ctypes.c_int

        self.__library_handle.T32_ReadRegister.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_ReadRegister.restype = ctypes.c_int

        self.__library_handle.T32_WriteRegister.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_WriteRegister.restype = ctypes.c_int

        self.__library_handle.T32_ReadBreakpoint.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.POINTER(ctypes.c_uint16), ctypes.c_int]
        self.__library_handle.T32_ReadBreakpoint.restype = ctypes.c_int

        self.__library_handle.T32_WriteBreakpoint.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.__library_handle.T32_WriteBreakpoint.restype = ctypes.c_int

        self.__library_handle.T32_GetBreakpointList.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_void_p, ctypes.c_int]
        self.__library_handle.T32_GetBreakpointList.restype = ctypes.c_int

        self.__library_handle.T32_GetTraceState.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]
        self.__library_handle.T32_GetTraceState.restype = ctypes.c_int

        self.__library_handle.T32_ReadTrace.argtypes = [ctypes.c_int, ctypes.c_int32, ctypes.c_int, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8)]
        self.__library_handle.T32_ReadTrace.restype = ctypes.c_int

        self.__library_handle.T32_GetLastErrorMessage.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetLastErrorMessage.restype = ctypes.c_int

        # self.__library_handle.T32_NotifyStateEnable.argtypes = [ctypes.c_int, None]
        # self.__library_handle.T32_NotifyStateEnable.restype = ctypes.c_int

        # self.__library_handle.T32_NotifyEventEnable.argtypes = [ctypes.c_char_p, None]
        # self.__library_handle.T32_NotifyEventEnable.restype = ctypes.c_int

        self.__library_handle.T32_CheckStateNotify.argtypes = [ctypes.c_uint]
        self.__library_handle.T32_CheckStateNotify.restype = ctypes.c_int

        self.__library_handle.T32_NotificationPending.argtypes = None
        self.__library_handle.T32_NotificationPending.restype = ctypes.c_int

        self.__library_handle.T32_AnaStatusGet.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]
        self.__library_handle.T32_AnaStatusGet.restype = ctypes.c_int

        self.__library_handle.T32_AnaRecordGet.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int]
        self.__library_handle.T32_AnaRecordGet.restype = ctypes.c_int

        self.__library_handle.T32_ReleaseAllObjects.argtypes = None
        self.__library_handle.T32_ReleaseAllObjects.restype = ctypes.c_int

        self.__library_handle.T32_RequestBufferObj.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
        self.__library_handle.T32_RequestBufferObj.restype = ctypes.c_int

        self.__library_handle.T32_ReleaseBufferObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_ReleaseBufferObj.restype = ctypes.c_int

        self.__library_handle.T32_ResizeBufferObj.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.__library_handle.T32_ResizeBufferObj.restype = ctypes.c_int

        self.__library_handle.T32_CopyDataFromBufferObj.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_int, ctypes.c_void_p]
        self.__library_handle.T32_CopyDataFromBufferObj.restype = ctypes.c_int

        self.__library_handle.T32_CopyDataToBufferObj.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8)]
        self.__library_handle.T32_CopyDataToBufferObj.restype = ctypes.c_int

        self.__library_handle.T32_GetBufferObjStoragePointer.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)), ctypes.c_void_p]
        self.__library_handle.T32_GetBufferObjStoragePointer.restype = ctypes.c_int

        self.__library_handle.T32_RequestAddressObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_RequestAddressObj.restype = ctypes.c_int

        self.__library_handle.T32_RequestAddressObjA32.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint32]
        self.__library_handle.T32_RequestAddressObjA32.restype = ctypes.c_int

        self.__library_handle.T32_RequestAddressObjA64.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint64]
        self.__library_handle.T32_RequestAddressObjA64.restype = ctypes.c_int

        self.__library_handle.T32_ReleaseAddressObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_ReleaseAddressObj.restype = ctypes.c_int

        self.__library_handle.T32_CopyAddressObj.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
        self.__library_handle.T32_CopyAddressObj.restype = ctypes.c_int

        self.__library_handle.T32_SetAddressObjAddr32.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_SetAddressObjAddr32.restype = ctypes.c_int

        self.__library_handle.T32_GetAddressObjAddr32.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetAddressObjAddr32.restype = ctypes.c_int

        self.__library_handle.T32_SetAddressObjAddr64.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        self.__library_handle.T32_SetAddressObjAddr64.restype = ctypes.c_int

        self.__library_handle.T32_GetAddressObjAddr64.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
        self.__library_handle.T32_GetAddressObjAddr64.restype = ctypes.c_int

        self.__library_handle.T32_SetAddressObjAccessString.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.__library_handle.T32_SetAddressObjAccessString.restype = ctypes.c_int

        self.__library_handle.T32_GetAddressObjAccessString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint8]
        self.__library_handle.T32_GetAddressObjAccessString.restype = ctypes.c_int

        self.__library_handle.T32_SetAddressObjWidth.argtypes = [ctypes.c_void_p, ctypes.c_uint16]
        self.__library_handle.T32_SetAddressObjWidth.restype = ctypes.c_int

        self.__library_handle.T32_SetAddressObjCore.argtypes = [ctypes.c_void_p, ctypes.c_uint16]
        self.__library_handle.T32_SetAddressObjCore.restype = ctypes.c_int

        self.__library_handle.T32_SetAddressObjSpaceId.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_SetAddressObjSpaceId.restype = ctypes.c_int

        self.__library_handle.T32_SetAddressObjAttr.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_SetAddressObjAttr.restype = ctypes.c_int

        #    self.__library_handle.T32_SetAddressObjSizeOfMau.argtypes = [ctypes.c_void_p, enum]
        #    self.__library_handle.T32_SetAddressObjSizeOfMau.restype = ctypes.c_int

        self.__library_handle.T32_GetAddressObjSizeOfMau.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.__library_handle.T32_GetAddressObjSizeOfMau.restype = ctypes.c_int

        self.__library_handle.T32_GetAddressObjTargetSizeOfMau.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.__library_handle.T32_GetAddressObjTargetSizeOfMau.restype = ctypes.c_int

        self.__library_handle.T32_QueryAddressObjMmuTranslation.argtypes = [ctypes.c_void_p, ctypes.c_uint16]
        self.__library_handle.T32_QueryAddressObjMmuTranslation.restype = ctypes.c_int

        self.__library_handle.T32_QueryAddressObjTargetSizeOfMau.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_QueryAddressObjTargetSizeOfMau.restype = ctypes.c_int

        #    self.__library_handle.T32_RequestRegisterObj.argtypes = [ctypes.POINTER(ctypes.c_void_p), enum]
        #    self.__library_handle.T32_RequestRegisterObj.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR32.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_RequestRegisterObjR32.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR64.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_RequestRegisterObjR64.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR128.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_RequestRegisterObjR128.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR256.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_RequestRegisterObjR256.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR512.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_RequestRegisterObjR512.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR32Name.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p]
        self.__library_handle.T32_RequestRegisterObjR32Name.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR64Name.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p]
        self.__library_handle.T32_RequestRegisterObjR64Name.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR128Name.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p]
        self.__library_handle.T32_RequestRegisterObjR128Name.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR256Name.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p]
        self.__library_handle.T32_RequestRegisterObjR256Name.restype = ctypes.c_int

        self.__library_handle.T32_RequestRegisterObjR512Name.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p]
        self.__library_handle.T32_RequestRegisterObjR512Name.restype = ctypes.c_int

        self.__library_handle.T32_ReleaseRegisterObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_ReleaseRegisterObj.restype = ctypes.c_int

        self.__library_handle.T32_SetRegisterObjName.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.__library_handle.T32_SetRegisterObjName.restype = ctypes.c_int

        self.__library_handle.T32_GetRegisterObjName.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint8]
        self.__library_handle.T32_GetRegisterObjName.restype = ctypes.c_int

        self.__library_handle.T32_SetRegisterObjId.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_SetRegisterObjId.restype = ctypes.c_int

        self.__library_handle.T32_GetRegisterObjId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetRegisterObjId.restype = ctypes.c_int

        self.__library_handle.T32_SetRegisterObjValue32.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_SetRegisterObjValue32.restype = ctypes.c_int

        self.__library_handle.T32_GetRegisterObjValue32.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetRegisterObjValue32.restype = ctypes.c_int

        self.__library_handle.T32_SetRegisterObjValue64.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        self.__library_handle.T32_SetRegisterObjValue64.restype = ctypes.c_int

        self.__library_handle.T32_GetRegisterObjValue64.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
        self.__library_handle.T32_GetRegisterObjValue64.restype = ctypes.c_int

        self.__library_handle.T32_SetRegisterObjValueArray.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8]
        self.__library_handle.T32_SetRegisterObjValueArray.restype = ctypes.c_int

        self.__library_handle.T32_GetRegisterObjValueArray.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint8]
        self.__library_handle.T32_GetRegisterObjValueArray.restype = ctypes.c_int

        self.__library_handle.T32_SetRegisterObjCore.argtypes = [ctypes.c_void_p, ctypes.c_uint16]
        self.__library_handle.T32_SetRegisterObjCore.restype = ctypes.c_int

        self.__library_handle.T32_GetRegisterObjCore.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint16)]
        self.__library_handle.T32_GetRegisterObjCore.restype = ctypes.c_int

        self.__library_handle.T32_RequestSymbolObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_RequestSymbolObj.restype = ctypes.c_int

        self.__library_handle.T32_RequestSymbolObjName.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p]
        self.__library_handle.T32_RequestSymbolObjName.restype = ctypes.c_int

        self.__library_handle.T32_RequestSymbolObjAddr.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
        self.__library_handle.T32_RequestSymbolObjAddr.restype = ctypes.c_int

        self.__library_handle.T32_ReleaseSymbolObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_ReleaseSymbolObj.restype = ctypes.c_int

        self.__library_handle.T32_SetSymbolObjName.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.__library_handle.T32_SetSymbolObjName.restype = ctypes.c_int

        self.__library_handle.T32_GetSymbolObjName.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint8]
        self.__library_handle.T32_GetSymbolObjName.restype = ctypes.c_int

        self.__library_handle.T32_GetSymbolObjNamePtr.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p)]
        self.__library_handle.T32_GetSymbolObjNamePtr.restype = ctypes.c_int

        self.__library_handle.T32_SetSymbolObjPath.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.__library_handle.T32_SetSymbolObjPath.restype = ctypes.c_int

        self.__library_handle.T32_GetSymbolObjPath.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint16)]
        self.__library_handle.T32_GetSymbolObjPath.restype = ctypes.c_int

        self.__library_handle.T32_GetSymbolObjPathPtr.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p)]
        self.__library_handle.T32_GetSymbolObjPathPtr.restype = ctypes.c_int

        self.__library_handle.T32_SetSymbolObjAddress.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.__library_handle.T32_SetSymbolObjAddress.restype = ctypes.c_int

        self.__library_handle.T32_GetSymbolObjAddress.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_GetSymbolObjAddress.restype = ctypes.c_int

        self.__library_handle.T32_GetSymbolObjSize.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
        self.__library_handle.T32_GetSymbolObjSize.restype = ctypes.c_int

        self.__library_handle.T32_RequestBreakpointObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_RequestBreakpointObj.restype = ctypes.c_int

        self.__library_handle.T32_RequestBreakpointObjAddr.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
        self.__library_handle.T32_RequestBreakpointObjAddr.restype = ctypes.c_int

        self.__library_handle.T32_ReleaseBreakpointObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_ReleaseBreakpointObj.restype = ctypes.c_int

        self.__library_handle.T32_SetBreakpointObjAddress.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.__library_handle.T32_SetBreakpointObjAddress.restype = ctypes.c_int

        self.__library_handle.T32_GetBreakpointObjAddress.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_GetBreakpointObjAddress.restype = ctypes.c_int

        self.__library_handle.T32_SetBreakpointObjType.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_SetBreakpointObjType.restype = ctypes.c_int

        self.__library_handle.T32_GetBreakpointObjType.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetBreakpointObjType.restype = ctypes.c_int

        self.__library_handle.T32_SetBreakpointObjImpl.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_SetBreakpointObjImpl.restype = ctypes.c_int

        self.__library_handle.T32_GetBreakpointObjImpl.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetBreakpointObjImpl.restype = ctypes.c_int

        self.__library_handle.T32_SetBreakpointObjAction.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_SetBreakpointObjAction.restype = ctypes.c_int

        self.__library_handle.T32_GetBreakpointObjAction.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetBreakpointObjAction.restype = ctypes.c_int

        self.__library_handle.T32_SetBreakpointObjEnable.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
        self.__library_handle.T32_SetBreakpointObjEnable.restype = ctypes.c_int

        self.__library_handle.T32_GetBreakpointObjEnable.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8)]
        self.__library_handle.T32_GetBreakpointObjEnable.restype = ctypes.c_int

        self.__library_handle.T32_RequestMemoryBundleObj.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
        self.__library_handle.T32_RequestMemoryBundleObj.restype = ctypes.c_int

        self.__library_handle.T32_ReleaseMemoryBundleObj.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        self.__library_handle.T32_ReleaseMemoryBundleObj.restype = ctypes.c_int

        self.__library_handle.T32_AddToBundleObjAddrLengthByteArray.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8)]
        self.__library_handle.T32_AddToBundleObjAddrLengthByteArray.restype = ctypes.c_int

        self.__library_handle.T32_AddToBundleObjAddrLength.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_AddToBundleObjAddrLength.restype = ctypes.c_int

        self.__library_handle.T32_GetBundleObjSize.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetBundleObjSize.restype = ctypes.c_int

        self.__library_handle.T32_GetBundleObjSyncStatusByIndex.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint32]
        self.__library_handle.T32_GetBundleObjSyncStatusByIndex.restype = ctypes.c_int

        self.__library_handle.T32_CopyDataFromBundleObjByIndex.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_CopyDataFromBundleObjByIndex.restype = ctypes.c_int

        self.__library_handle.T32_TransferMemoryBundleObj.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_TransferMemoryBundleObj.restype = ctypes.c_int

        self.__library_handle.T32_ReadMemoryObj.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_ReadMemoryObj.restype = ctypes.c_int

        self.__library_handle.T32_WriteMemoryObj.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_WriteMemoryObj.restype = ctypes.c_int

        self.__library_handle.T32_ReadRegisterObj.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_ReadRegisterObj.restype = ctypes.c_int

        self.__library_handle.T32_WriteRegisterObj.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_WriteRegisterObj.restype = ctypes.c_int

        self.__library_handle.T32_QuerySymbolObj.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_QuerySymbolObj.restype = ctypes.c_int

        self.__library_handle.T32_WriteBreakpointObj.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.__library_handle.T32_WriteBreakpointObj.restype = ctypes.c_int

        self.__library_handle.T32_QueryBreakpointObjCount.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_QueryBreakpointObjCount.restype = ctypes.c_int

        self.__library_handle.T32_ReadBreakpointObj.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_ReadBreakpointObj.restype = ctypes.c_int

        self.__library_handle.T32_ReadBreakpointObjByIndex.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.__library_handle.T32_ReadBreakpointObjByIndex.restype = ctypes.c_int

        self.__library_handle.T32_Fdx_Resolve.argtypes = [ctypes.c_char_p]
        self.__library_handle.T32_Fdx_Resolve.restype = ctypes.c_int

        self.__library_handle.T32_Fdx_Open.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.__library_handle.T32_Fdx_Open.restype = ctypes.c_int

        self.__library_handle.T32_Fdx_Close.argtypes = [ctypes.c_int]
        self.__library_handle.T32_Fdx_Close.restype = ctypes.c_int

        self.__library_handle.T32_Fdx_Receive.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.__library_handle.T32_Fdx_Receive.restype = ctypes.c_int

        self.__library_handle.T32_Fdx_ReceivePoll.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.__library_handle.T32_Fdx_ReceivePoll.restype = ctypes.c_int

        self.__library_handle.T32_Fdx_Send.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.__library_handle.T32_Fdx_Send.restype = ctypes.c_int

        self.__library_handle.T32_Fdx_SendPoll.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.__library_handle.T32_Fdx_SendPoll.restype = ctypes.c_int

        #    self.__library_handle.T32_ParamFromUint32.argtypes = [ctypes.c_uint32]
        #    self.__library_handle.T32_ParamFromUint32.restype = union

        self.__library_handle.T32_BundledAccessAlloc.argtypes = None
        self.__library_handle.T32_BundledAccessAlloc.restype = ctypes.c_void_p

        self.__library_handle.T32_BundledAccessExecute.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.__library_handle.T32_BundledAccessExecute.restype = ctypes.c_int

        self.__library_handle.T32_BundledAccessFree.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_BundledAccessFree.restype = ctypes.c_int

        self.__library_handle.T32_DirectAccessRelease.argtypes = None
        self.__library_handle.T32_DirectAccessRelease.restype = ctypes.c_int

        self.__library_handle.T32_DirectAccessResetAll.argtypes = [ctypes.c_void_p]
        self.__library_handle.T32_DirectAccessResetAll.restype = ctypes.c_int

        #    self.__library_handle.T32_DirectAccessSetInfo.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_int, union]
        #    self.__library_handle.T32_DirectAccessSetInfo.restype = ctypes.c_int

        self.__library_handle.T32_DirectAccessGetInfo.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p]
        self.__library_handle.T32_DirectAccessGetInfo.restype = ctypes.c_int

        self.__library_handle.T32_DirectAccessGetTimestamp.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)]
        self.__library_handle.T32_DirectAccessGetTimestamp.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessSetInfo.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.__library_handle.T32_TAPAccessSetInfo.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessSetInfo2.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.__library_handle.T32_TAPAccessSetInfo2.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessShiftRaw.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8),
                                                                ctypes.c_int]
        self.__library_handle.T32_TAPAccessShiftRaw.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessShiftIR.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8)]
        self.__library_handle.T32_TAPAccessShiftIR.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessShiftDR.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8)]
        self.__library_handle.T32_TAPAccessShiftDR.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessJTAGResetWithTMS.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self.__library_handle.T32_TAPAccessJTAGResetWithTMS.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessJTAGResetWithTRST.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int32, ctypes.c_int32]
        self.__library_handle.T32_TAPAccessJTAGResetWithTRST.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessSetShiftPattern.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                                                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint]
        self.__library_handle.T32_TAPAccessSetShiftPattern.restype = ctypes.c_int

        self.__library_handle.T32_TAPAccessDirect.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8)]
        self.__library_handle.T32_TAPAccessDirect.restype = ctypes.c_int

        self.__library_handle.T32_DirectAccessUserSignal.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_DirectAccessUserSignal.restype = ctypes.c_int

        self.__library_handle.T32_DAPAccessScan.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_DAPAccessScan.restype = ctypes.c_int

        self.__library_handle.T32_DAPAccessInitSWD.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self.__library_handle.T32_DAPAccessInitSWD.restype = ctypes.c_int

        self.__library_handle.T32_DAPAPAccessReadWrite.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint,
                                                                   ctypes.c_uint, ctypes.c_int, ctypes.c_uint32]
        self.__library_handle.T32_DAPAPAccessReadWrite.restype = ctypes.c_int

        self.__library_handle.T32_I2CAccess.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint, ctypes.POINTER(ctypes.c_uint8),
                                                        ctypes.c_uint]
        self.__library_handle.T32_I2CAccess.restype = ctypes.c_int

        self.__library_handle.T32_I2CRawAccess.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.c_int]
        self.__library_handle.T32_I2CRawAccess.restype = ctypes.c_int

        self.__library_handle.T32_DirectAccessExecuteLua.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int, ctypes.POINTER(ctypes.c_uint8),
                                                                     ctypes.c_int]
        self.__library_handle.T32_DirectAccessExecuteLua.restype = ctypes.c_int

        self.__library_handle.T32_ExecuteLua.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int]
        self.__library_handle.T32_ExecuteLua.restype = ctypes.c_int

        self.__library_handle.T32_Exp.argtypes = [ctypes.c_char_p, ctypes.c_uint16, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint16)]
        self.__library_handle.T32_Exp.restype = ctypes.c_int

    def __del__(self):
        if self.__library_handle is not None:
            self.t32_releaseallobjects()

    @property
    def library_handle(self):
        return self.__library_handle

    @decorator_error
    def t32_config(self, *args, **kwargs):
        return self.__library_handle.T32_Config(*args, **kwargs)

    @decorator_error
    def t32_init(self, *args, **kwargs):
        return self.__library_handle.T32_Init(*args, **kwargs)

    @decorator_error
    def t32_attach(self, *args, **kwargs):
        return self.__library_handle.T32_Attach(*args, **kwargs)

    @decorator_error
    def t32_terminate(self, *args, **kwargs):
        return self.__library_handle.T32_Terminate(*args, **kwargs)

    @decorator_error
    def t32_exit(self, *args, **kwargs):
        return self.__library_handle.T32_Exit(*args, **kwargs)

    @decorator_error
    def t32_ping(self, *args, **kwargs):
        return self.__library_handle.T32_Ping(*args, **kwargs)

    @decorator_error
    def t32_nop(self, *args, **kwargs):
        return self.__library_handle.T32_Nop(*args, **kwargs)

    @decorator_error
    def t32_nopex(self, *args, **kwargs):
        return self.__library_handle.T32_NopEx(*args, **kwargs)

    @decorator_error
    def t32_nopfail(self, *args, **kwargs):
        return self.__library_handle.T32_NopFail(*args, **kwargs)

    @decorator_error
    def t32_cmd(self, *args, **kwargs):
        return self.__library_handle.T32_Cmd(*args, **kwargs)

    @decorator_error
    def t32_executecommand(self, *args, **kwargs):
        return self.__library_handle.T32_ExecuteCommand(*args, **kwargs)

    @decorator_error
    def t32_executefunction(self, *args, **kwargs):
        return self.__library_handle.T32_ExecuteFunction(*args, **kwargs)

    @decorator_error
    def t32_printf(self, *args, **kwargs):
        return self.__library_handle.T32_Printf(*args, **kwargs)

    @decorator_error
    def t32_stop(self, *args, **kwargs):
        return self.__library_handle.T32_Stop(*args, **kwargs)

    @decorator_error
    def t32_getpracticestate(self, *args, **kwargs):
        return self.__library_handle.T32_GetPracticeState(*args, **kwargs)

    @decorator_error
    def t32_evalget(self, *args, **kwargs):
        return self.__library_handle.T32_EvalGet(*args, **kwargs)

    @decorator_error
    def t32_evalgetstring(self, *args, **kwargs):
        return self.__library_handle.T32_EvalGetString(*args, **kwargs)

    @decorator_error
    def t32_getmessage(self, *args, **kwargs):
        return self.__library_handle.T32_GetMessage(*args, **kwargs)

    @decorator_error
    def t32_gettriggermessage(self, *args, **kwargs):
        return self.__library_handle.T32_GetTriggerMessage(*args, **kwargs)

    @decorator_error
    def t32_getchannelsize(self, *args, **kwargs):
        return self.__library_handle.T32_GetChannelSize(*args, **kwargs)

    @decorator_error
    def t32_getchanneldefaults(self, *args, **kwargs):
        return self.__library_handle.T32_GetChannelDefaults(*args, **kwargs)

    @decorator_error
    def t32_setchannel(self, *args, **kwargs):
        return self.__library_handle.T32_SetChannel(*args, **kwargs)

    @decorator_error
    def t32_apilock(self, *args, **kwargs):
        return self.__library_handle.T32_APILock(*args, **kwargs)

    @decorator_error
    def t32_apiunlock(self, *args, **kwargs):
        return self.__library_handle.T32_APIUnlock(*args, **kwargs)

    @decorator_error
    def t32_getapirevision(self, *args, **kwargs):
        self.__library_handle.T32_GetApiRevision.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        self.__library_handle.T32_GetApiRevision.restype = ctypes.c_int
        return self.__library_handle.T32_GetApiRevision(*args, **kwargs)

    @decorator_error
    def t32_getsockethandle(self, *args, **kwargs):
        return self.__library_handle.T32_GetSocketHandle(*args, **kwargs)

    @decorator_error
    def t32_go(self, *args, **kwargs):
        return self.__library_handle.T32_Go(*args, **kwargs)

    @decorator_error
    def t32_break(self, *args, **kwargs):
        return self.__library_handle.T32_Break(*args, **kwargs)

    @decorator_error
    def t32_step(self, *args, **kwargs):
        return self.__library_handle.T32_Step(*args, **kwargs)

    @decorator_error
    def t32_stepmode(self, *args, **kwargs):
        return self.__library_handle.T32_StepMode(*args, **kwargs)

    @decorator_error
    def t32_resetcpu(self, *args, **kwargs):
        return self.__library_handle.T32_ResetCPU(*args, **kwargs)

    @decorator_error
    def t32_setmode(self, *args, **kwargs):
        return self.__library_handle.T32_SetMode(*args, **kwargs)

    @decorator_error
    def t32_getcpuinfo(self, *args, **kwargs):
        return self.__library_handle.T32_GetCpuInfo(*args, **kwargs)

    @decorator_error
    def t32_getstate(self, *args, **kwargs):
        return self.__library_handle.T32_GetState(*args, **kwargs)

    @decorator_error
    def t32_readmemory(self, *args, **kwargs):
        return self.__library_handle.T32_ReadMemory(*args, **kwargs)

    @decorator_error
    def t32_writememory(self, *args, **kwargs):
        return self.__library_handle.T32_WriteMemory(*args, **kwargs)

    @decorator_error
    def t32_writememorypipe(self, *args, **kwargs):
        return self.__library_handle.T32_WriteMemoryPipe(*args, **kwargs)

    @decorator_error
    def t32_readmemoryex(self, *args, **kwargs):
        return self.__library_handle.T32_ReadMemoryEx(*args, **kwargs)

    @decorator_error
    def t32_writememoryex(self, *args, **kwargs):
        return self.__library_handle.T32_WriteMemoryEx(*args, **kwargs)

    @decorator_error
    def t32_setmemoryaccessclass(self, *args, **kwargs):
        return self.__library_handle.T32_SetMemoryAccessClass(*args, **kwargs)

    @decorator_error
    def t32_getram(self, *args, **kwargs):
        return self.__library_handle.T32_GetRam(*args, **kwargs)

    @decorator_error
    def t32_getsource(self, *args, **kwargs):
        return self.__library_handle.T32_GetSource(*args, **kwargs)

    @decorator_error
    def t32_getselectedsource(self, *args, **kwargs):
        return self.__library_handle.T32_GetSelectedSource(*args, **kwargs)

    @decorator_error
    def t32_getsymbol(self, *args, **kwargs):
        return self.__library_handle.T32_GetSymbol(*args, **kwargs)

    @decorator_error
    def t32_getsymbolfromaddress(self, *args, **kwargs):
        return self.__library_handle.T32_GetSymbolFromAddress(*args, **kwargs)

    @decorator_error
    def t32_readvariablestring(self, *args, **kwargs):
        return self.__library_handle.T32_ReadVariableString(*args, **kwargs)

    @decorator_error
    def t32_readvariablevalue(self, *args, **kwargs):
        return self.__library_handle.T32_ReadVariableValue(*args, **kwargs)

    @decorator_error
    def t32_writevariablevalue(self, *args, **kwargs):
        return self.__library_handle.T32_WriteVariableValue(*args, **kwargs)

    @decorator_error
    def t32_getwindowcontent(self, *args, **kwargs):
        return self.__library_handle.T32_GetWindowContent(*args, **kwargs)

    @decorator_error
    def t32_readregisterbyname(self, *args, **kwargs):
        return self.__library_handle.T32_ReadRegisterByName(*args, **kwargs)

    @decorator_error
    def t32_writeregisterbyname(self, *args, **kwargs):
        return self.__library_handle.T32_WriteRegisterByName(*args, **kwargs)

    @decorator_error
    def t32_readpp(self, *args, **kwargs):
        return self.__library_handle.T32_ReadPP(*args, **kwargs)

    @decorator_error
    def t32_readregister(self, *args, **kwargs):
        return self.__library_handle.T32_ReadRegister(*args, **kwargs)

    @decorator_error
    def t32_writeregister(self, *args, **kwargs):
        return self.__library_handle.T32_WriteRegister(*args, **kwargs)

    @decorator_error
    def t32_readbreakpoint(self, *args, **kwargs):
        return self.__library_handle.T32_ReadBreakpoint(*args, **kwargs)

    @decorator_error
    def t32_writebreakpoint(self, *args, **kwargs):
        return self.__library_handle.T32_WriteBreakpoint(*args, **kwargs)

    @decorator_error
    def t32_getbreakpointlist(self, *args, **kwargs):
        return self.__library_handle.T32_GetBreakpointList(*args, **kwargs)

    @decorator_error
    def t32_gettracestate(self, *args, **kwargs):
        return self.__library_handle.T32_GetTraceState(*args, **kwargs)

    @decorator_error
    def t32_readtrace(self, *args, **kwargs):
        return self.__library_handle.T32_ReadTrace(*args, **kwargs)

    @decorator_error
    def t32_getlasterrormessage(self, *args, **kwargs):
        return self.__library_handle.T32_GetLastErrorMessage(*args, **kwargs)

    @decorator_error
    def t32_notifystateenable(self, *args, **kwargs):
        return self.__library_handle.T32_NotifyStateEnable(*args, **kwargs)

    @decorator_error
    def t32_notifyeventenable(self, *args, **kwargs):
        return self.__library_handle.T32_NotifyEventEnable(*args, **kwargs)

    @decorator_error
    def t32_checkstatenotify(self, *args, **kwargs):
        return self.__library_handle.T32_CheckStateNotify(*args, **kwargs)

    @decorator_error
    def t32_notificationpending(self, *args, **kwargs):
        return self.__library_handle.T32_NotificationPending(*args, **kwargs)

    @decorator_error
    def t32_anastatusget(self, *args, **kwargs):
        return self.__library_handle.T32_AnaStatusGet(*args, **kwargs)

    @decorator_error
    def t32_anarecordget(self, *args, **kwargs):
        return self.__library_handle.T32_AnaRecordGet(*args, **kwargs)

    @decorator_error
    def t32_releaseallobjects(self, *args, **kwargs):
        return self.__library_handle.T32_ReleaseAllObjects(*args, **kwargs)

    @decorator_error
    def t32_requestbufferobj(self, *args, **kwargs):
        return self.__library_handle.T32_RequestBufferObj(*args, **kwargs)

    @decorator_error
    def t32_releasebufferobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReleaseBufferObj(*args, **kwargs)

    @decorator_error
    def t32_resizebufferobj(self, *args, **kwargs):
        return self.__library_handle.T32_ResizeBufferObj(*args, **kwargs)

    @decorator_error
    def t32_copydatafrombufferobj(self, *args, **kwargs):
        return self.__library_handle.T32_CopyDataFromBufferObj(*args, **kwargs)

    @decorator_error
    def t32_copydatatobufferobj(self, *args, **kwargs):
        return self.__library_handle.T32_CopyDataToBufferObj(*args, **kwargs)

    @decorator_error
    def t32_getbufferobjstoragepointer(self, *args, **kwargs):
        return self.__library_handle.T32_GetBufferObjStoragePointer(*args, **kwargs)

    @decorator_error
    def t32_requestaddressobj(self, *args, **kwargs):
        return self.__library_handle.T32_RequestAddressObj(*args, **kwargs)

    @decorator_error
    def t32_requestaddressobja32(self, *args, **kwargs):
        return self.__library_handle.T32_RequestAddressObjA32(*args, **kwargs)

    @decorator_error
    def t32_requestaddressobja64(self, *args, **kwargs):
        return self.__library_handle.T32_RequestAddressObjA64(*args, **kwargs)

    @decorator_error
    def t32_releaseaddressobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReleaseAddressObj(*args, **kwargs)

    @decorator_error
    def t32_copyaddressobj(self, *args, **kwargs):
        return self.__library_handle.T32_CopyAddressObj(*args, **kwargs)

    @decorator_error
    def t32_setaddressobjaddr32(self, *args, **kwargs):
        return self.__library_handle.T32_SetAddressObjAddr32(*args, **kwargs)

    @decorator_error
    def t32_getaddressobjaddr32(self, *args, **kwargs):
        return self.__library_handle.T32_GetAddressObjAddr32(*args, **kwargs)

    @decorator_error
    def t32_setaddressobjaddr64(self, *args, **kwargs):
        return self.__library_handle.T32_SetAddressObjAddr64(*args, **kwargs)

    @decorator_error
    def t32_getaddressobjaddr64(self, *args, **kwargs):
        return self.__library_handle.T32_GetAddressObjAddr64(*args, **kwargs)

    @decorator_error
    def t32_setaddressobjaccessstring(self, *args, **kwargs):
        return self.__library_handle.T32_SetAddressObjAccessString(*args, **kwargs)

    @decorator_error
    def t32_getaddressobjaccessstring(self, *args, **kwargs):
        return self.__library_handle.T32_GetAddressObjAccessString(*args, **kwargs)

    @decorator_error
    def t32_setaddressobjwidth(self, *args, **kwargs):
        return self.__library_handle.T32_SetAddressObjWidth(*args, **kwargs)

    @decorator_error
    def t32_setaddressobjcore(self, *args, **kwargs):
        return self.__library_handle.T32_SetAddressObjCore(*args, **kwargs)

    @decorator_error
    def t32_setaddressobjspaceid(self, *args, **kwargs):
        return self.__library_handle.T32_SetAddressObjSpaceId(*args, **kwargs)

    @decorator_error
    def t32_setaddressobjattr(self, *args, **kwargs):
        return self.__library_handle.T32_SetAddressObjAttr(*args, **kwargs)

    @decorator_error
    def t32_setaddressobjsizeofmau(self, *args, **kwargs):
        return self.__library_handle.T32_SetAddressObjSizeOfMau(*args, **kwargs)

    @decorator_error
    def t32_getaddressobjsizeofmau(self, *args, **kwargs):
        return self.__library_handle.T32_GetAddressObjSizeOfMau(*args, **kwargs)

    @decorator_error
    def t32_getaddressobjtargetsizeofmau(self, *args, **kwargs):
        return self.__library_handle.T32_GetAddressObjTargetSizeOfMau(*args, **kwargs)

    @decorator_error
    def t32_queryaddressobjmmutranslation(self, *args, **kwargs):
        return self.__library_handle.T32_QueryAddressObjMmuTranslation(*args, **kwargs)

    @decorator_error
    def t32_queryaddressobjtargetsizeofmau(self, *args, **kwargs):
        return self.__library_handle.T32_QueryAddressObjTargetSizeOfMau(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobj(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObj(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr32(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR32(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr64(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR64(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr128(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR128(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr256(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR256(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr512(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR512(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr32name(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR32Name(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr64name(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR64Name(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr128name(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR128Name(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr256name(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR256Name(*args, **kwargs)

    @decorator_error
    def t32_requestregisterobjr512name(self, *args, **kwargs):
        return self.__library_handle.T32_RequestRegisterObjR512Name(*args, **kwargs)

    @decorator_error
    def t32_releaseregisterobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReleaseRegisterObj(*args, **kwargs)

    @decorator_error
    def t32_setregisterobjname(self, *args, **kwargs):
        return self.__library_handle.T32_SetRegisterObjName(*args, **kwargs)

    @decorator_error
    def t32_getregisterobjname(self, *args, **kwargs):
        return self.__library_handle.T32_GetRegisterObjName(*args, **kwargs)

    @decorator_error
    def t32_setregisterobjid(self, *args, **kwargs):
        return self.__library_handle.T32_SetRegisterObjId(*args, **kwargs)

    @decorator_error
    def t32_getregisterobjid(self, *args, **kwargs):
        return self.__library_handle.T32_GetRegisterObjId(*args, **kwargs)

    @decorator_error
    def t32_setregisterobjvalue32(self, *args, **kwargs):
        return self.__library_handle.T32_SetRegisterObjValue32(*args, **kwargs)

    @decorator_error
    def t32_getregisterobjvalue32(self, *args, **kwargs):
        return self.__library_handle.T32_GetRegisterObjValue32(*args, **kwargs)

    @decorator_error
    def t32_setregisterobjvalue64(self, *args, **kwargs):
        return self.__library_handle.T32_SetRegisterObjValue64(*args, **kwargs)

    @decorator_error
    def t32_getregisterobjvalue64(self, *args, **kwargs):
        return self.__library_handle.T32_GetRegisterObjValue64(*args, **kwargs)

    @decorator_error
    def t32_setregisterobjvaluearray(self, *args, **kwargs):
        return self.__library_handle.T32_SetRegisterObjValueArray(*args, **kwargs)

    @decorator_error
    def t32_getregisterobjvaluearray(self, *args, **kwargs):
        return self.__library_handle.T32_GetRegisterObjValueArray(*args, **kwargs)

    @decorator_error
    def t32_setregisterobjcore(self, *args, **kwargs):
        return self.__library_handle.T32_SetRegisterObjCore(*args, **kwargs)

    @decorator_error
    def t32_getregisterobjcore(self, *args, **kwargs):
        return self.__library_handle.T32_GetRegisterObjCore(*args, **kwargs)

    @decorator_error
    def t32_requestsymbolobj(self, *args, **kwargs):
        return self.__library_handle.T32_RequestSymbolObj(*args, **kwargs)

    @decorator_error
    def t32_requestsymbolobjname(self, *args, **kwargs):
        return self.__library_handle.T32_RequestSymbolObjName(*args, **kwargs)

    @decorator_error
    def t32_requestsymbolobjaddr(self, *args, **kwargs):
        return self.__library_handle.T32_RequestSymbolObjAddr(*args, **kwargs)

    @decorator_error
    def t32_releasesymbolobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReleaseSymbolObj(*args, **kwargs)

    @decorator_error
    def t32_setsymbolobjname(self, *args, **kwargs):
        return self.__library_handle.T32_SetSymbolObjName(*args, **kwargs)

    @decorator_error
    def t32_getsymbolobjname(self, *args, **kwargs):
        return self.__library_handle.T32_GetSymbolObjName(*args, **kwargs)

    @decorator_error
    def t32_getsymbolobjnameptr(self, *args, **kwargs):
        return self.__library_handle.T32_GetSymbolObjNamePtr(*args, **kwargs)

    @decorator_error
    def t32_setsymbolobjpath(self, *args, **kwargs):
        return self.__library_handle.T32_SetSymbolObjPath(*args, **kwargs)

    @decorator_error
    def t32_getsymbolobjpath(self, *args, **kwargs):
        return self.__library_handle.T32_GetSymbolObjPath(*args, **kwargs)

    @decorator_error
    def t32_getsymbolobjpathptr(self, *args, **kwargs):
        return self.__library_handle.T32_GetSymbolObjPathPtr(*args, **kwargs)

    @decorator_error
    def t32_setsymbolobjaddress(self, *args, **kwargs):
        return self.__library_handle.T32_SetSymbolObjAddress(*args, **kwargs)

    @decorator_error
    def t32_getsymbolobjaddress(self, *args, **kwargs):
        return self.__library_handle.T32_GetSymbolObjAddress(*args, **kwargs)

    @decorator_error
    def t32_getsymbolobjsize(self, *args, **kwargs):
        return self.__library_handle.T32_GetSymbolObjSize(*args, **kwargs)

    @decorator_error
    def t32_requestbreakpointobj(self, *args, **kwargs):
        return self.__library_handle.T32_RequestBreakpointObj(*args, **kwargs)

    @decorator_error
    def t32_requestbreakpointobjaddr(self, *args, **kwargs):
        return self.__library_handle.T32_RequestBreakpointObjAddr(*args, **kwargs)

    @decorator_error
    def t32_releasebreakpointobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReleaseBreakpointObj(*args, **kwargs)

    @decorator_error
    def t32_setbreakpointobjaddress(self, *args, **kwargs):
        return self.__library_handle.T32_SetBreakpointObjAddress(*args, **kwargs)

    @decorator_error
    def t32_getbreakpointobjaddress(self, *args, **kwargs):
        return self.__library_handle.T32_GetBreakpointObjAddress(*args, **kwargs)

    @decorator_error
    def t32_setbreakpointobjtype(self, *args, **kwargs):
        return self.__library_handle.T32_SetBreakpointObjType(*args, **kwargs)

    @decorator_error
    def t32_getbreakpointobjtype(self, *args, **kwargs):
        return self.__library_handle.T32_GetBreakpointObjType(*args, **kwargs)

    @decorator_error
    def t32_setbreakpointobjimpl(self, *args, **kwargs):
        return self.__library_handle.T32_SetBreakpointObjImpl(*args, **kwargs)

    @decorator_error
    def t32_getbreakpointobjimpl(self, *args, **kwargs):
        return self.__library_handle.T32_GetBreakpointObjImpl(*args, **kwargs)

    @decorator_error
    def t32_setbreakpointobjaction(self, *args, **kwargs):
        return self.__library_handle.T32_SetBreakpointObjAction(*args, **kwargs)

    @decorator_error
    def t32_getbreakpointobjaction(self, *args, **kwargs):
        return self.__library_handle.T32_GetBreakpointObjAction(*args, **kwargs)

    @decorator_error
    def t32_setbreakpointobjenable(self, *args, **kwargs):
        return self.__library_handle.T32_SetBreakpointObjEnable(*args, **kwargs)

    @decorator_error
    def t32_getbreakpointobjenable(self, *args, **kwargs):
        return self.__library_handle.T32_GetBreakpointObjEnable(*args, **kwargs)

    @decorator_error
    def t32_requestmemorybundleobj(self, *args, **kwargs):
        return self.__library_handle.T32_RequestMemoryBundleObj(*args, **kwargs)

    @decorator_error
    def t32_releasememorybundleobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReleaseMemoryBundleObj(*args, **kwargs)

    @decorator_error
    def t32_addtobundleobjaddrlengthbytearray(self, *args, **kwargs):
        return self.__library_handle.T32_AddToBundleObjAddrLengthByteArray(*args, **kwargs)

    @decorator_error
    def t32_addtobundleobjaddrlength(self, *args, **kwargs):
        return self.__library_handle.T32_AddToBundleObjAddrLength(*args, **kwargs)

    @decorator_error
    def t32_getbundleobjsize(self, *args, **kwargs):
        return self.__library_handle.T32_GetBundleObjSize(*args, **kwargs)

    @decorator_error
    def t32_getbundleobjsyncstatusbyindex(self, *args, **kwargs):
        return self.__library_handle.T32_GetBundleObjSyncStatusByIndex(*args, **kwargs)

    @decorator_error
    def t32_copydatafrombundleobjbyindex(self, *args, **kwargs):
        return self.__library_handle.T32_CopyDataFromBundleObjByIndex(*args, **kwargs)

    @decorator_error
    def t32_transfermemorybundleobj(self, *args, **kwargs):
        return self.__library_handle.T32_TransferMemoryBundleObj(*args, **kwargs)

    @decorator_error
    def t32_readmemoryobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReadMemoryObj(*args, **kwargs)

    @decorator_error
    def t32_writememoryobj(self, *args, **kwargs):
        return self.__library_handle.T32_WriteMemoryObj(*args, **kwargs)

    @decorator_error
    def t32_readregisterobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReadRegisterObj(*args, **kwargs)

    @decorator_error
    def t32_exp(self, *args, **kwargs):
        return self.__library_handle.T32_Exp(*args, **kwargs)

    @decorator_error
    def t32_writeregisterobj(self, *args, **kwargs):
        return self.__library_handle.T32_WriteRegisterObj(*args, **kwargs)

    @decorator_error
    def t32_querysymbolobj(self, *args, **kwargs):
        return self.__library_handle.T32_QuerySymbolObj(*args, **kwargs)

    @decorator_error
    def t32_writebreakpointobj(self, *args, **kwargs):
        return self.__library_handle.T32_WriteBreakpointObj(*args, **kwargs)

    @decorator_error
    def t32_querybreakpointobjcount(self, *args, **kwargs):
        return self.__library_handle.T32_QueryBreakpointObjCount(*args, **kwargs)

    @decorator_error
    def t32_readbreakpointobj(self, *args, **kwargs):
        return self.__library_handle.T32_ReadBreakpointObj(*args, **kwargs)

    @decorator_error
    def t32_readbreakpointobjbyindex(self, *args, **kwargs):
        return self.__library_handle.T32_ReadBreakpointObjByIndex(*args, **kwargs)

    @decorator_error
    def t32_fdx_resolve(self, *args, **kwargs):
        return self.__library_handle.T32_Fdx_Resolve(*args, **kwargs)

    @decorator_error
    def t32_fdx_open(self, *args, **kwargs):
        return self.__library_handle.T32_Fdx_Open(*args, **kwargs)

    @decorator_error
    def t32_fdx_close(self, *args, **kwargs):
        return self.__library_handle.T32_Fdx_Close(*args, **kwargs)

    @decorator_error
    def t32_fdx_receive(self, *args, **kwargs):
        return self.__library_handle.T32_Fdx_Receive(*args, **kwargs)

    @decorator_error
    def t32_fdx_receivepoll(self, *args, **kwargs):
        return self.__library_handle.T32_Fdx_ReceivePoll(*args, **kwargs)

    @decorator_error
    def t32_fdx_send(self, *args, **kwargs):
        return self.__library_handle.T32_Fdx_Send(*args, **kwargs)

    @decorator_error
    def t32_fdx_sendpoll(self, *args, **kwargs):
        return self.__library_handle.T32_Fdx_SendPoll(*args, **kwargs)

    @decorator_error
    def t32_paramfromuint32(self, *args, **kwargs):
        return self.__library_handle.T32_ParamFromUint32(*args, **kwargs)

    @decorator_error
    def t32_bundledaccessalloc(self, *args, **kwargs):
        return self.__library_handle.T32_BundledAccessAlloc(*args, **kwargs)

    @decorator_error
    def t32_bundledaccessexecute(self, *args, **kwargs):
        return self.__library_handle.T32_BundledAccessExecute(*args, **kwargs)

    @decorator_error
    def t32_bundledaccessfree(self, *args, **kwargs):
        return self.__library_handle.T32_BundledAccessFree(*args, **kwargs)

    @decorator_error
    def t32_directaccessrelease(self, *args, **kwargs):
        return self.__library_handle.T32_DirectAccessRelease(*args, **kwargs)

    @decorator_error
    def t32_directaccessresetall(self, *args, **kwargs):
        return self.__library_handle.T32_DirectAccessResetAll(*args, **kwargs)

    @decorator_error
    def t32_directaccesssetinfo(self, *args, **kwargs):
        return self.__library_handle.T32_DirectAccessSetInfo(*args, **kwargs)

    @decorator_error
    def t32_directaccessgetinfo(self, *args, **kwargs):
        return self.__library_handle.T32_DirectAccessGetInfo(*args, **kwargs)

    @decorator_error
    def t32_directaccessgettimestamp(self, *args, **kwargs):
        return self.__library_handle.T32_DirectAccessGetTimestamp(*args, **kwargs)

    @decorator_error
    def t32_tapaccesssetinfo(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessSetInfo(*args, **kwargs)

    @decorator_error
    def t32_tapaccesssetinfo2(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessSetInfo2(*args, **kwargs)

    @decorator_error
    def t32_tapaccessshiftraw(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessShiftRaw(*args, **kwargs)

    @decorator_error
    def t32_tapaccessshiftir(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessShiftIR(*args, **kwargs)

    @decorator_error
    def t32_tapaccessshiftdr(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessShiftDR(*args, **kwargs)

    @decorator_error
    def t32_tapaccessjtagresetwithtms(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessJTAGResetWithTMS(*args, **kwargs)

    @decorator_error
    def t32_tapaccessjtagresetwithtrst(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessJTAGResetWithTRST(*args, **kwargs)

    @decorator_error
    def t32_tapaccesssetshiftpattern(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessSetShiftPattern(*args, **kwargs)

    @decorator_error
    def t32_tapaccessdirect(self, *args, **kwargs):
        return self.__library_handle.T32_TAPAccessDirect(*args, **kwargs)

    @decorator_error
    def t32_directaccessusersignal(self, *args, **kwargs):
        return self.__library_handle.T32_DirectAccessUserSignal(*args, **kwargs)

    @decorator_error
    def t32_dapaccessscan(self, *args, **kwargs):
        return self.__library_handle.T32_DAPAccessScan(*args, **kwargs)

    @decorator_error
    def t32_dapaccessinitswd(self, *args, **kwargs):
        return self.__library_handle.T32_DAPAccessInitSWD(*args, **kwargs)

    @decorator_error
    def t32_dapapaccessreadwrite(self, *args, **kwargs):
        return self.__library_handle.T32_DAPAPAccessReadWrite(*args, **kwargs)

    @decorator_error
    def t32_i2caccess(self, *args, **kwargs):
        return self.__library_handle.T32_I2CAccess(*args, **kwargs)

    @decorator_error
    def t32_i2crawaccess(self, *args, **kwargs):
        return self.__library_handle.T32_I2CRawAccess(*args, **kwargs)

    @decorator_error
    def t32_directaccessexecutelua(self, *args, **kwargs):
        return self.__library_handle.T32_DirectAccessExecuteLua(*args, **kwargs)

    @decorator_error
    def t32_executelua(self, *args, **kwargs):
        return self.__library_handle.T32_ExecuteLua(*args, **kwargs)

    @decorator_error
    def t32_exp(self, *args, **kwargs):
        return self.__library_handle.T32_Exp(*args, **kwargs)

    def get_handle(self):
        return self.__library_handle

    @staticmethod
    def auto_detect_library_name():
        if (platform.system() == 'Windows') or (platform.system()[0:6] == 'CYGWIN'):
            if ctypes.sizeof(ctypes.c_voidp) == 4:
                return 't32api.dll'  # WINDOWS 32bit
            else:
                return 't32api64.dll'  # WINDOWS 64bit
        elif platform.system() == 'Darwin':
            return 't32api.dylib'  # Mac OS X
        else:
            if ctypes.sizeof(ctypes.c_voidp) == 4:
                return 't32api.so'  # Linux 32bit
            else:
                return 't32api64.so'  # Linux 64bit

    def __check_api_version(self):
        global _API_VERSION_MIN
        c_api_version = ctypes.c_uint32()
        self.t32_getapirevision(c_api_version)
        api_version = c_api_version.value
        if api_version < _API_VERSION_MIN:
            raise ApiVersionError('Minimum required API version: {}, current API version {}'.format(_API_VERSION_MIN, api_version))
        print('API version: {}'.format(api_version))
