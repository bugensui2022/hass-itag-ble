from homeassistant.components.select import SelectEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN, MODES

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ITagModeSelect(coord, entry)])

class ITagModeSelect(SelectEntity, RestoreEntity):
    def __init__(self, coord, entry):
        self._coord = coord
        self._attr_unique_id = f"{entry.data['address']}_mode"
        self._attr_device_info = coord.device_info
        self._attr_name = "工作模式"
        self._attr_options = list(MODES.keys())

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state and state.state in MODES:
            self._coord.current_mode = state.state
            self._attr_current_option = state.state

    async def async_select_option(self, option: str):
        self._coord.current_mode = option
        self._attr_current_option = option
        # 👈 此时调用 __init__.py 中补全的 send_cmd 就不会报错了
        await self._coord.send_cmd(MODES[option])
        self.async_write_ha_state()