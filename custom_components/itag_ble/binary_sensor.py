from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ITagConn(coord, entry)])

class ITagConn(BinarySensorEntity):
    def __init__(self, coord, entry):
        self._coord = coord
        self._attr_unique_id = f"{entry.data['address']}_conn"
        self._attr_device_info = coord.device_info
        self._attr_name = "在线状态"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    @property
    def is_on(self): return self._coord.connected