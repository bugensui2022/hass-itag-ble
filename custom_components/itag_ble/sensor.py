from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ITagBat(coord, entry), 
        ITagAct(coord, entry),
        ITagSource(coord, entry) # 👈 连接节点显示
    ])

class ITagSensorBase(SensorEntity):
    def __init__(self, coord, entry):
        self._coord = coord
        self._attr_device_info = coord.device_info
    async def async_added_to_hass(self):
        self._coord.add_listener(self.async_write_ha_state)

class ITagBat(ITagSensorBase):
    def __init__(self, coord, entry):
        super().__init__(coord, entry)
        self._attr_unique_id = f"{entry.data['address']}_bat"
        self._attr_name = "电池电量"
        self._attr_device_class = "battery"
        self._attr_native_unit_of_measurement = "%"
    @property
    def native_value(self): return self._coord.battery

class ITagAct(ITagSensorBase):
    def __init__(self, coord, entry):
        super().__init__(coord, entry)
        self._attr_unique_id = f"{entry.data['address']}_act"
        self._attr_name = "最后动作"
        self._attr_icon = "mdi:gesture-tap"
    @property
    def native_value(self): return self._coord.last_action

class ITagSource(ITagSensorBase):
    def __init__(self, coord, entry):
        super().__init__(coord, entry)
        self._attr_unique_id = f"{entry.data['address']}_source"
        self._attr_name = "连接节点"
        self._attr_icon = "mdi:bluetooth-connect"
    @property
    def native_value(self): return self._coord.connection_source