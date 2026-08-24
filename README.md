# Home Assistant iTag BLE 自定义集成 (itag_ble)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

本项目是将市面上极高性价比（约 2.9 元）的 **iTag 蓝牙防丢器** 接入 Home Assistant 的全功能自定义集成（Custom Integration）。

通过深度结合 Home Assistant 官方的 **蓝牙代理（Bluetooth Proxy）** 技术，彻底打破了以往将 iTag 固定绑定在单个 ESP32 设备上的局限，实现了在多房间、多 ESP32 蓝牙网关之间的 **无缝漫游、自动重连与状态同步**。

---

## 🆚 为什么选择集成方案（对比 ESPHome 直接绑定）

| 对比维度 | ESPHome 单设备绑定方案 | 本集成方案（HA 自定义集成 + 蓝牙代理） |
| :--- | :--- | :--- |
| **覆盖范围** | 仅限绑定的单台 ESP32 覆盖范围 | **全屋无缝漫游**（只要有 ESP32 代理覆盖的区域均可响应） |
| **设备添加** | 每次添加新 iTag 都需修改 YAML 并重新烧录固件 | **纯 HA UI 界面配置**，仅需输入 MAC 地址即可完成添加与热修改 |
| **漫游切换** | 跨房间信号衰减后容易直接断连失效 | **自动感知断开并毫秒级重连**到就近最强信号网关 |
| **节点感知** | 无法获知当前连在哪个物理位置 | **提供连接节点传感器**，实时显示当前连接的 ESP32 友好名称 |
| **防吵闹处理** | 容易在上电/重连瞬间发出蜂鸣误报 | **内置静音初始化握手**，断连重连均静音无感 |

---

## ✨ 核心功能与特性

1. **🏠 全屋蓝牙漫游**：
   - 支持多台 ESP32 Bluetooth Proxy 与 HA 本机蓝牙适配器协同工作。
   - 随身携带钥匙扣在各房间走动时，集成会自动切换至信号最佳的蓝牙节点。

2. **👆 智能双击/单击手势识别**：
   - 内置 600ms 智能观察窗口与硬件消抖算法，精准区分 **单击** 与 **双击**。
   - 同步通过实体状态更新与系统事件总线（`itag_ble_event`）双通道触发，方便自动化编写。

3. **📡 网关节点感知与追踪**：
   - 提供专属的“连接节点”传感器，自动联查 HA 设备注册表，显示具体网关名称（如 `客厅蓝牙网关`、`卧室 ESP32` 或 `本机适配器`）。

4. **🔋 低功耗电池电量监控**：
   - 采用 2 小时低频轮询机制，既能精准掌握 CR2032 纽扣电池剩余电量，又将对电池寿命的影响降到最低。

5. **🔇 工作模式自由切换**：
   - 支持通过下拉菜单实体实时切换工作模式：
     - **静音模式**：日常作为无线开关使用，无蜂鸣打扰。
     - **寻物模式**：触发防丢器蜂鸣器持续发声，用于快速寻找钥匙/物品。
     - **按键音模式**：按下按键时伴随蜂鸣反馈。

6. **🛡️ 健壮的防睡死与重连机制**：
   - 针对廉价 BLE 芯片协议栈简单的特点，加入了断开瞬时回调（`disconnected_callback`）与超时强保，彻底解决漫游过程中的设备休眠睡死问题。

---

## 📂 项目结构说明

```text
custom_components/itag_ble/
├── __init__.py          # 核心调度器：蓝牙连接、漫游切换、断线重连与后台任务管理
├── config_flow.py      # 配置流向导：支持 UI 添加与热修改 MAC 地址（防 500 崩溃设计）
├── const.py            # 常量与 GATT 特征码定义
├── sensor.py           # 传感器平台：电池电量、最后动作、连接节点
├── binary_sensor.py    # 二元传感器平台：蓝牙在线状态
├── select.py           # 选择器平台：工作模式切换（静音/寻物/按键音）
├── manifest.json       # 集成元数据清单文件
└── strings.json        # 多语言文本与配置向导界面定义
```

---

## 📥 安装步骤

### 方法一：通过 HACS 自定义存储库安装（推荐）

1. 确保您的 Home Assistant 已安装 [HACS](https://hacs.xyz/)。
2. 打开 **HACS** -> 点击右上角 **三个点** -> 选择 **自定义存储库 (Custom repositories)**。
3. 在存储库地址中输入您的 GitHub 仓库 URL：
   `https://github.com/您的用户名/您的仓库名`
4. 类别 (Category) 选择 **集成 (Integration)**，点击 **添加**。
5. 在列表中找到 **iTag BLE Integration**，点击 **下载**。
6. **重启 Home Assistant**。

---

### 方法二：手动文件夹拷贝安装

1. 点击本仓库右上角的 **Code** -> **Download ZIP** 下载项目压缩包。
2. 解压后，将 `custom_components/itag_ble` 整个文件夹复制到 Home Assistant 的配置目录下的 `custom_components` 中。
   * 目录完整路径示范：
     ```text
     /config/custom_components/itag_ble/
     ```
3. **重启 Home Assistant**。

---

## ⚙️ 配置与添加设备

1. 确保你的 iTag 防丢器装上电池并长按按键 3 秒开机（听到开机提示音）。
2. 在 Home Assistant 中进入 **设置** -> **设备与服务**。
3. 点击右下角 **添加集成**，在搜索框输入 `iTag`。
4. 在弹出的配置框中输入你的 iTag **蓝牙 MAC 地址**（格式如：`FF:EE:DD:CC:BB:AA`）。
5. 点击提交，集成将自动完成蓝牙发现、握手与实体创建。

> 💡 **提示**：如果后续更换了新的 iTag 设备，可在集成卡片中点击 **配置 (Configure)** 直接修改 MAC 地址，无需删除重建。

---

## 📊 实体与属性一览

添加成功后，系统会生成一个专属的 iTag 设备以及以下实体：

| 实体名称 | 实体 ID 格式 | 类型 | 说明 / 可选值 |
| :--- | :--- | :--- | :--- |
| **最后动作** | `sensor.itag_xxxx_act` | `sensor` | `单击`、`双击`、`null` |
| **连接节点** | `sensor.itag_xxxx_source` | `sensor` | 当前负责通信的网关名称（如 `客厅网关`） |
| **电池电量** | `sensor.itag_xxxx_bat` | `sensor` | 当前电量百分比（`0%` ~ `100%`） |
| **工作模式** | `select.itag_xxxx_mode` | `select` | `静音模式`、`寻物模式`、`按键提示音` |
| **在线状态** | `binary_sensor.itag_xxxx_status` | `binary_sensor` | `连接` (on) / `断开` (off) |

---

## 🤖 自动化配置示例 (YAML)

### 示例 1：通过事件（Event）触发自动化（推荐，响应最快）

每次点击都会向 HA 事件总线发送 `itag_ble_event` 事件：

```yaml
alias: "iTag 按键控制客厅灯"
description: "单击开灯，双击全关"
trigger:
  - platform: event
    event_type: itag_ble_event
    event_data:
      address: "FF:EE:DD:CC:BB:AA" # 你的 iTag MAC 地址
condition: []
action:
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.action == 'single' }}"
        sequence:
          - target:
              entity_id: light.living_room_light
            action: light.toggle
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.action == 'double' }}"
        sequence:
          - target:
              entity_id: all
            action: light.turn_off
mode: restart
```

---

### 示例 2：低电量通知自动化

```yaml
alias: "iTag 低电量更换提醒"
trigger:
  - platform: numeric_state
    entity_id: sensor.itag_xxxx_bat
    below: 20
action:
  - action: notify.persistent_notification
    data:
      title: "钥匙扣电量过低"
      message: "iTag 防丢器电量已低于 20%，请及时更换 CR2032 电池！"
```

---

## ❓ 常见问题 (FAQ)

#### Q1: 按下按键后，为什么在 HA 里看到状态改变会有约 1.5 ~ 2 秒的延迟？
> **答**：这是正常现象。
> 1. **双击判定窗口**：为了区分单击与双击，程序必须设定 600ms 的观察窗口，等待用户是否会按下第二次。
> 2. **网络链路转发**：iTag 蓝牙 -> ESP32 代理节点 -> Wi-Fi 传回 HA -> 状态写入 -> 前端 WebSocket 刷新，整条链路在 1.5 秒左右是分布式蓝牙网关架构下的正常水平。

#### Q2: 连接节点显示的是一段 MAC 地址而不是网关名字？
> **答**：本集成会自动抓取你在 ESPHome 中给 ESP32 节点配置的名称。请在 HA 的 **设备与服务 -> ESPHome** 中确认该设备已有可读的友好名称。

#### Q3: 如何获取 iTag 的 MAC 地址？
> **答**：手机下载并打开 **nRF Connect** APP，或在电脑上开启蓝牙扫描，将 iTag 按键开机后靠近手机，即可在扫描列表中找到名为 `iTag` / `BLE Tag` 的设备及其 MAC 地址。

---

## 📄 开源许可

本项目基于 [MIT License](LICENSE) 开源。欢迎提交 PR、Issue 或分享你的自动化玩法！
