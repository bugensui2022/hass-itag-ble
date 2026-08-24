import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class ITagConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理 iTag 的主配置流程。"""
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            address = user_input["address"].upper()
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"iTag {address}", data={"address": address})
        
        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({vol.Required("address"): str})
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """返回选项流处理器。"""
        return ITagOptionsFlow(config_entry)

class ITagOptionsFlow(config_entries.OptionsFlow):
    """处理 iTag 的选项流"""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """初始化选项流，显式存储 config_entry。"""
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        """选项流初始化步骤。"""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        # 👈 核心修复：显式使用初始化时存储的 self._entry
        options = self._entry.options
        data = self._entry.data
        
        # 动态获取当前 MAC，提供占位默认值
        current_address = options.get("address", data.get("address", "FF:FF:FF:FF:FF:FF"))
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("address", default=str(current_address)): str
            })
        )