# Home Assistant iTag BLE 自定义集成 (itag_ble)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Home Assistant](https://img.shields.io/badge/Home--Assistant-Integration-blue.svg)

本项目旨在将市场上极其廉价（约2.9元）的 **iTag 蓝牙防丢器** 完美接入 Home Assistant。

与传统的 ESPHome 直接绑定方案不同，本集成利用 HA 的 **蓝牙代理（Bluetooth Proxy）** 技术，实现了 iTag 在全屋不同 ESP32 节点之间的 **无缝漫游**。

---

## 🌟 核心特性

- 🏠 **全屋漫游**：无需固定绑定某个 ESP32。只要有蓝牙代理覆盖的地方，iTag 就能自动重连并生效。
- 👆 **精准手势**：内置算法加固，支持 **单击** 和 **双击** 动作识别（带 600ms 智能判定窗口）。
- 📡 **节点感知**：实时显示当前 iTag 连接的物理节点名称（例如：显示“客厅蓝牙网关”）。
- 🔋 **电量监控**：实时读取 CR2032 电池电量百分比，避免关键时刻掉链子。
- 🔇 **模式切换**：支持“寻物蜂鸣”、“按键提示音”和“静音模式”实时切换。
- ⚙️ **极简配置**：纯 UI 操作，无需编写任何 YAML 代码，只需输入 MAC 地址。

---

## 🛠️ 硬件要求

1. **iTag 硬件**：市面常见的水滴形低功耗蓝牙防丢器。
2. **蓝牙代理网关**：至少一个刷入 ESPHome 蓝牙代理固件的 ESP32 节点（建议全屋布置以实现漫游）。

---

## 📂 项目结构

```text
custom_components/itag_ble/
├── __init__.py          # 核心连接管理与漫游逻辑
├── config_flow.py      # 配置向导（支持修改 MAC 与 500 错误防护）
├── const.py            # 特征码及常量定义
├── sensor.py           # 电池、最后动作、连接节点传感器
├── binary_sensor.py    # 在线状态实体
├── select.py           # 工作模式切换实体
└── manifest.json       # 集成元数据
