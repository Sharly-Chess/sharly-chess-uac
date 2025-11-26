import winreg
from typing import Literal, Any
from winreg import HKEYType


class WinRegistryUtils:
    @classmethod
    def _set_registry_value(
        cls,
        key: HKEYType | int,
        sub_key: str,
        name: str,
        type: Literal[4, 5] | int,
        value: Any,
    ) -> bool:
        """Sets the value of an entry of the registry, returns True on success, False on failure"""
        try:
            winreg.CreateKey(key, sub_key)
            registry_key = winreg.OpenKey(
                key,
                sub_key,
                0,
                winreg.KEY_WRITE,
            )
            winreg.SetValueEx(
                registry_key,
                name,
                0,
                type,
                value,
            )
            winreg.CloseKey(registry_key)
            return True
        except WindowsError as we:
            print(
                f'{cls.__name__}._set_registry_value(key=[{key}], sub_key=[{sub_key}], name=[{name}], value=[{value}]) raised an error: {we}'
            )
            return False

    @classmethod
    def _set_registry_hklm_value(
        cls,
        sub_key: str,
        name: str,
        type: Literal[4, 5] | int,
        value: Any,
    ) -> bool:
        return cls._set_registry_value(
            winreg.HKEY_LOCAL_MACHINE, sub_key, name, type, value
        )

    @classmethod
    def set_registry_hklm_dword(
        cls,
        sub_key: str,
        name: str,
        value: Any,
    ) -> bool:
        return cls._set_registry_hklm_value(sub_key, name, winreg.REG_DWORD, value)

    @classmethod
    def _get_registry_value(
        cls,
        key: HKEYType | int,
        sub_key: str,
        name: str,
    ) -> Any:
        try:
            registry_key = winreg.OpenKey(
                key,
                sub_key,
                0,
                winreg.KEY_READ,
            )
            value, regtype = winreg.QueryValueEx(registry_key, name)
            winreg.CloseKey(registry_key)
            return value
        except WindowsError as we:
            print(
                f'{cls.__name__}._get_registry_value(key=[{key}], sub_key=[{sub_key}], name=[{name}]) raised an error: {we}'
            )
            return None

    @classmethod
    def get_registry_hklm_value(
        cls,
        sub_key: str,
        name: str,
    ) -> Any:
        return cls._get_registry_value(winreg.HKEY_LOCAL_MACHINE, sub_key, name)

    @classmethod
    def get_registry_hkcu_value(
        cls,
        sub_key: str,
        name: str,
    ) -> Any:
        return cls._get_registry_value(winreg.HKEY_CURRENT_USER, sub_key, name)

    @classmethod
    def _get_registry_values(
        cls,
        key: HKEYType | int,
        sub_key: str,
    ) -> dict[str, Any]:
        key_dict = {}
        i = 0
        try:
            registry_key = winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ)
            while True:
                try:
                    subvalue = winreg.EnumValue(registry_key, i)
                except WindowsError:
                    break
                key_dict[subvalue[0]] = subvalue[1:]
                i += 1
            return key_dict
        except WindowsError as we:
            print(
                f'{cls.__name__}._get_registry_values(key=[{key}], sub_key=[{sub_key}]) raised an error: {we}'
            )
            return key_dict

    @classmethod
    def get_registry_hklm_values(
        cls,
        sub_key: str,
    ) -> dict[str, Any]:
        return cls._get_registry_values(winreg.HKEY_LOCAL_MACHINE, sub_key)

    @classmethod
    def get_registry_hkcu_values(
        cls,
        sub_key: str,
    ) -> dict[str, Any]:
        return cls._get_registry_values(winreg.HKEY_CURRENT_USER, sub_key)
