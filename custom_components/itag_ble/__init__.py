import asyncio
import logging
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import bluetooth
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry as dr
from bleak import BleakClient
from bleak_retry_connector import establish_connection

from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # 动态获取当前配置的 MAC 地址
    address = entry.options.get("address", entry.data.get("address")).upper()
    
    class ITagCoordinator:
        def __init__(self):
            self.client = None
            self.battery = 0
            self.last_action = "null"
            self.connected = False
            self.current_mode = "静音模式"
            self.connection_source = "查找中..."
            self._click_task = None
            self._listeners = []
            self._last_battery_time = 0
            # 🌟 新增：手动唤醒触发器
            self._connect_trigger = asyncio.Event()

        def add_listener(self, cb): self._listeners.append(cb)
        
        def update(self): [cb() for cb in self._listeners]

        @property
        def device_info(self) -> DeviceInfo:
            return DeviceInfo(
                identifiers={(DOMAIN, address)},
                name=f"iTag ({address})",
                manufacturer=MANUFACTURER,
                model="iTag Pro"
            )

        def _on_disconnect(self, client: BleakClient):
            """链路一旦断开（如漫游超出范围），立即标记并触发重连循环"""
            _LOGGER.debug(f"iTag {address} 链路已断开，准备重新寻找节点")
            self.connected = False
            self.client = None
            self.update()

        # 🌟 新增：由按键调用的强制连接方法
        def force_connect(self):
            if not self.connected:
                _LOGGER.debug(f"接收到手动指令，正在强制唤醒 iTag {address} 连接进程")
                self._connect_trigger.set()

        # 🌟 新增：带有中断唤醒功能的智能休眠
        async def _smart_sleep(self, delay):
            try:
                await asyncio.wait_for(self._connect_trigger.wait(), timeout=delay)
                # 如果是被按钮唤醒的，清除标志位，直接放行
                self._connect_trigger.clear()
            except asyncio.TimeoutError:
                # 正常时间到了，放行
                pass

        async def send_cmd(self, val):
            if self.client and self.client.is_connected:
                try:
                    await asyncio.wait_for(self.client.write_gatt_char(CHR_ALERT_LEVEL, bytes([val])), timeout=3.0)
                except Exception as e:
                    _LOGGER.error(f"指令发送失败: {e}")

        async def _reset_act(self):
            await asyncio.sleep(0.5)
            self.last_action = "null"
            self.update()

        async def _handle_click_timer(self):
            """判定窗口定时器 (600ms)"""
            await asyncio.sleep(0.6)
            self.last_action = "单击"
            self.update()
            hass.bus.async_fire("itag_ble_event", {"address": address, "action": "single"})
            self._click_task = None
            hass.async_create_task(self._reset_act())

        def _on_notify(self, handle, data):
            if data and data[0] == 0x01:
                if self._click_task:
                    self._click_task.cancel()
                    self._click_task = None
                    self.last_action = "双击"
                    self.update()
                    hass.bus.async_fire("itag_ble_event", {"address": address, "action": "double"})
                    hass.async_create_task(self._reset_act())
                else:
                    self._click_task = hass.async_create_task(self._handle_click_timer())

        async def run(self):
            while True:
                # 1. 扫描寻找设备
                ble_device = bluetooth.async_ble_device_from_address(hass, address)
                if not ble_device:
                    # 🌟 替换：使用智能休眠，允许随时被按钮打断
                    await self._smart_sleep(3)
                    continue
                
                # 2. 节点名称解析
                source_id = ble_device.details.get("source", "local")
                if source_id == "local":
                    self.connection_source = "本机适配器"
                else:
                    registry = dr.async_get(hass)
                    found_name = False
                    for device in registry.devices.values():
                        if any(source_id.upper() == str(c[1]).upper() for c in device.connections if len(c) > 1):
                            self.connection_source = device.name_by_user or device.name
                            found_name = True
                            break
                    if not found_name:
                        scanner = bluetooth.async_scanner_by_source(hass, source_id)
                        self.connection_source = scanner.name if scanner else f"网关 ({source_id})"
                
                try:
                    # 3. 连接加固
                    client = await establish_connection(
                        BleakClient,
                        ble_device,
                        address,
                        disconnected_callback=self._on_disconnect
                    )
                    
                    async with client:
                        self.client = client
                        self.connected = True
                        self.update()
                        
                        # 4. 初始化序列
                        try:
                            await asyncio.wait_for(client.write_gatt_char(CHR_ITAG_ANTI_LOSS, b"\x00"), timeout=4.0)
                            await asyncio.wait_for(self.client.write_gatt_char(CHR_ALERT_LEVEL, bytes([MODES.get(self.current_mode, 0x02)])), timeout=4.0)
                        except: pass
                        
                        await client.start_notify(CHR_ITAG_NOTIFY, self._on_notify)
                        
                        # 5. 心跳监控
                        while client.is_connected:
                            now = time.time()
                            if now - self._last_battery_time > 7200:
                                try:
                                    bat = await asyncio.wait_for(client.read_gatt_char(CHR_BATTERY_LEVEL), timeout=5.0)
                                    self.battery = bat[0] if bat else self.battery
                                    self._last_battery_time = now
                                    self.update()
                                except: pass
                            await asyncio.sleep(1)
                except Exception as e:
                    self.connected = False
                    self.update()
                    _LOGGER.debug(f"iTag 连接失败或正在漫游: {e}")
                    # 🌟 替换：使用智能休眠，允许随时被按钮打断
                    await self._smart_sleep(2)

    coord = ITagCoordinator()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coord
    
    entry.async_create_background_task(hass, coord.run(), "itag_ble_loop")
    
    # 🌟 修改：平台列表中加入了 "button"
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "select", "button"])
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # 🌟 修改：平台列表中加入了 "button"
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor", "select", "button"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
