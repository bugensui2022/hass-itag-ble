from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """设置 Button 平台"""
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ITagForceConnectButton(coord)])

class ITagForceConnectButton(ButtonEntity):
    """触发强制连接的实体按钮"""
    
    _attr_has_entity_name = True
    _attr_name = "强制主动连接"
    _attr_icon = "mdi:bluetooth-connect"

    def __init__(self, coord):
        self.coord = coord
        mac_addr = list(coord.device_info["identifiers"])[0][1]
        self._attr_unique_id = f"{mac_addr}_force_connect"
        self._attr_device_info = coord.device_info

    async def async_press(self) -> None:
        """当用户在前端点击按钮时触发"""
        self.coord.force_connect()
