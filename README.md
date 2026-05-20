<p align="center">
  <h1 align="center">🧘 DevRitual</h1>
  <p align="center">
    <strong>轻量级终端开发者仪式感与习惯养成引擎</strong><br>
    Lightweight Terminal Developer Ritual & Habit Building Engine
  </p>
  <p align="center">
    <a href="#-简体中文">简体中文</a> ·
    <a href="#-繁體中文">繁體中文</a> ·
    <a href="#-english">English</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/Dependencies-Zero-green.svg" alt="Zero Dependencies">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
    <img src="https://img.shields.io/badge/Tests-69%20Passed-brightgreen.svg" alt="Tests">
  </p>
</p>

---

# 🇨🇳 简体中文

## 🎉 项目介绍

**DevRitual** 是一款专为开发者打造的轻量级终端仪式感与习惯养成引擎。它帮助你在终端中建立和追踪编程习惯、定义每日仪式感流程，并通过精美的统计可视化来激励你持续进步。

### 💡 灵感来源

作为开发者，我们每天面对大量代码和任务，很容易陷入无序的工作节奏。DevRitual 的灵感来源于「仪式感」理念——通过为日常开发流程赋予仪式感，帮助开发者建立高效、可持续的工作习惯。无论是晨间代码审查、提交前检查清单，还是每日学习打卡，DevRitual 都能帮你系统化管理。

### 🌟 自研差异化亮点

- **零外部依赖**：纯 Python 标准库实现，无需安装任何第三方包
- **本地优先**：所有数据存储在本地 JSON 文件中，隐私安全
- **内置模板**：提供 8 个仪式模板 + 8 个习惯模板，开箱即用
- **热力图日历**：终端 ASCII 渲染的 GitHub 风格热力图
- **连续天数追踪**：自动计算习惯打卡的连续天数和最长记录

## ✨ 核心特性

- 🎯 **仪式管理** — 创建/编辑/删除/开始/完成/跳过仪式，支持模板快速创建
- 📅 **习惯追踪** — 每日打卡、连续天数自动计算、最长记录追踪
- 📊 **统计分析** — 每日/每周/每月完成率、排行榜、趋势分析
- 🗓️ **热力图日历** — 终端 ASCII 渲染的 GitHub 风格活动热力图
- 📈 **趋势图表** — 周对比柱状图、完成率趋势折线图
- 🖥️ **TUI 仪表盘** — 今日进度、待办清单、连续天数概览、快速统计
- 💾 **数据管理** — JSON 本地存储、导入/导出、自动备份与恢复
- 🎨 **ANSI 彩色输出** — 美观的终端彩色界面
- 📋 **预设模板** — 8 个仪式模板 + 8 个习惯模板，覆盖常见开发场景
- 🔒 **隐私优先** — 所有数据本地存储，不上传任何云端

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip（Python 包管理器）

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/DevRitual.git
cd DevRitual

# 安装（开发模式）
pip install -e .
```

### 快速上手

```bash
# 第一步：初始化配置
devritual init

# 第二步：使用模板创建一个仪式
devritual ritual create --template morning-review

# 第三步：创建一个习惯
devritual habit create --name "每日阅读技术文章" --frequency daily

# 第四步：开始仪式
devritual ritual start "晨间代码审查"

# 第五步：完成仪式
devritual ritual complete "晨间代码审查"

# 第六步：习惯打卡
devritual habit checkin "每日阅读技术文章"

# 第七步：查看仪表盘
devritual dashboard

# 第八步：查看统计热力图
devritual stats calendar
```

## 📖 详细使用指南

### 仪式管理

```bash
# 创建自定义仪式（交互式）
devritual ritual create

# 使用模板创建仪式
devritual ritual create --template morning-review
devritual ritual create --template pre-commit
devritual ritual create --template daily-standup
devritual ritual create --template weekly-retro
devritual ritual create --template code-review
devritual ritual create --template deploy-checklist
devritual ritual create --template learning-session
devritual ritual create --template end-of-day

# 列出所有仪式
devritual ritual list

# 开始执行仪式
devritual ritual start "晨间代码审查"

# 完成仪式
devritual ritual complete "晨间代码审查"

# 跳过今日仪式
devritual ritual skip "晨间代码审查"

# 删除仪式
devritual ritual delete "晨间代码审查"
```

### 习惯追踪

```bash
# 创建习惯（交互式）
devritual habit create

# 快速创建习惯
devritual habit create --name "写单元测试" --frequency daily
devritual habit create --name "代码重构" --frequency weekly

# 列出所有习惯
devritual habit list

# 打卡
devritual habit checkin "写单元测试"

# 查看连续天数
devritual habit streak "写单元测试"

# 删除习惯
devritual habit delete "写单元测试"
```

### 统计分析

```bash
# 查看综合统计
devritual stats

# 查看热力图日历
devritual stats calendar

# 查看趋势分析
devritual stats trend
```

### 数据管理

```bash
# 导出数据
devritual export

# 导入数据
devritual import backup.json

# 查看仪表盘
devritual dashboard
```

## 💡 设计思路与迭代规划

### 设计理念

DevRitual 的核心理念是「**让好习惯变得可视化**」。通过将抽象的习惯养成过程转化为具体的数据和图表，开发者可以清晰地看到自己的进步轨迹，从而获得持续的动力。

### 技术选型

- **Python 标准库**：确保零依赖，降低安装门槛
- **JSON 存储**：轻量级、可读性强、易于备份和迁移
- **ANSI 转义码**：无需额外依赖即可实现彩色终端输出
- **argparse**：Python 内置的命令行解析库，稳定可靠

### 后续迭代计划

- [ ] 🔔 自定义提醒功能（系统通知）
- [ ] 📊 更多统计图表（雷达图、饼图）
- [ ] 🌐 Web 仪表盘（本地 HTTP 服务）
- [ ] 🔗 Git 集成（自动追踪提交习惯）
- [ ] 📱 数据同步（多设备间同步）
- [ ] 🎮 成就系统（解锁徽章和里程碑）

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'feat: 添加某个特性'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 提交规范

- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

# 🇹🇼 繁體中文

## 🎉 專案介紹

**DevRitual** 是一款專為開發者打造的輕量級終端儀式感與習慣養成引擎。它幫助你在終端中建立和追蹤程式設計習慣、定義每日儀式感流程，並透過精美的統計視覺化來激勵你持續進步。

### 💡 靈感來源

作為開發者，我們每天面對大量程式碼和任務，很容易陷入無序的工作節奏。DevRitual 的靈感來源於「儀式感」理念——透過為日常開發流程賦予儀式感，幫助開發者建立高效、可持續的工作習慣。無論是晨間程式碼審查、提交前檢查清單，還是每日學習打卡，DevRitual 都能幫你系統化管理。

### 🌟 自研差異化亮點

- **零外部依賴**：純 Python 標準庫實現，無需安裝任何第三方套件
- **本地優先**：所有資料儲存在本地 JSON 檔案中，隱私安全
- **內建模板**：提供 8 個儀式模板 + 8 個習慣模板，開箱即用
- **熱力圖日曆**：終端 ASCII 渲染的 GitHub 風格熱力圖
- **連續天數追蹤**：自動計算習慣打卡的連續天數和最長記錄

## ✨ 核心特性

- 🎯 **儀式管理** — 建立/編輯/刪除/開始/完成/跳過儀式，支援模板快速建立
- 📅 **習慣追蹤** — 每日打卡、連續天數自動計算、最長記錄追蹤
- 📊 **統計分析** — 每日/每週/每月完成率、排行榜、趨勢分析
- 🗓️ **熱力圖日曆** — 終端 ASCII 渲染的 GitHub 風格活動熱力圖
- 📈 **趨勢圖表** — 週對比柱狀圖、完成率趨勢折線圖
- 🖥️ **TUI 儀表板** — 今日進度、待辦清單、連續天數概覽、快速統計
- 💾 **資料管理** — JSON 本地儲存、匯入/匯出、自動備份與復原
- 🎨 **ANSI 彩色輸出** — 美觀的終端彩色介面
- 📋 **預設模板** — 8 個儀式模板 + 8 個習慣模板，涵蓋常見開發場景
- 🔒 **隱私優先** — 所有資料本地儲存，不上傳任何雲端

## 🚀 快速開始

### 環境要求

- Python 3.8 或更高版本
- pip（Python 套件管理器）

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/DevRitual.git
cd DevRitual

# 安裝（開發模式）
pip install -e .
```

### 快速上手

```bash
# 第一步：初始化配置
devritual init

# 第二步：使用模板建立一個儀式
devritual ritual create --template morning-review

# 第三步：建立一個習慣
devritual habit create --name "每日閱讀技術文章" --frequency daily

# 第四步：開始儀式
devritual ritual start "晨間程式碼審查"

# 第五步：完成儀式
devritual ritual complete "晨間程式碼審查"

# 第六步：習慣打卡
devritual habit checkin "每日閱讀技術文章"

# 第七步：查看儀表板
devritual dashboard

# 第八步：查看統計熱力圖
devritual stats calendar
```

## 📖 詳細使用指南

### 儀式管理

```bash
# 建立自訂儀式（互動式）
devritual ritual create

# 使用模板建立儀式
devritual ritual create --template morning-review
devritual ritual create --template pre-commit
devritual ritual create --template daily-standup
devritual ritual create --template weekly-retro
devritual ritual create --template code-review
devritual ritual create --template deploy-checklist
devritual ritual create --template learning-session
devritual ritual create --template end-of-day

# 列出所有儀式
devritual ritual list

# 開始執行儀式
devritual ritual start "晨間程式碼審查"

# 完成儀式
devritual ritual complete "晨間程式碼審查"

# 跳過今日儀式
devritual ritual skip "晨間程式碼審查"

# 刪除儀式
devritual ritual delete "晨間程式碼審查"
```

### 習慣追蹤

```bash
# 建立習慣（互動式）
devritual habit create

# 快速建立習慣
devritual habit create --name "寫單元測試" --frequency daily
devritual habit create --name "程式碼重構" --frequency weekly

# 列出所有習慣
devritual habit list

# 打卡
devritual habit checkin "寫單元測試"

# 查看連續天數
devritual habit streak "寫單元測試"

# 刪除習慣
devritual habit delete "寫單元測試"
```

### 統計分析

```bash
# 查看綜合統計
devritual stats

# 查看熱力圖日曆
devritual stats calendar

# 查看趨勢分析
devritual stats trend
```

### 資料管理

```bash
# 匯出資料
devritual export

# 匯入資料
devritual import backup.json

# 查看儀表板
devritual dashboard
```

## 💡 設計思路與迭代規劃

### 設計理念

DevRitual 的核心理念是「**讓好習慣變得視覺化**」。透過將抽象的習慣養成過程轉化為具體的資料和圖表，開發者可以清晰地看到自己的進步軌跡，從而獲得持續的動力。

### 技術選型

- **Python 標準庫**：確保零依賴，降低安裝門檻
- **JSON 儲存**：輕量級、可讀性強、易於備份和遷移
- **ANSI 跳脫碼**：無需額外依賴即可實現彩色終端輸出
- **argparse**：Python 內建的命令列解析庫，穩定可靠

### 後續迭代計畫

- [ ] 🔔 自訂提醒功能（系統通知）
- [ ] 📊 更多統計圖表（雷達圖、圓餅圖）
- [ ] 🌐 Web 儀表板（本地 HTTP 服務）
- [ ] 🔗 Git 整合（自動追蹤提交習慣）
- [ ] 📱 資料同步（多裝置間同步）
- [ ] 🎮 成就系統（解鎖徽章和里程碑）

## 🤝 貢獻指南

歡迎貢獻程式碼！請遵循以下步驟：

1. Fork 本倉庫
2. 建立特性分支：`git checkout -b feature/amazing-feature`
3. 提交變更：`git commit -m 'feat: 新增某個特性'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 提交規範

- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具相關

## 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

# 🇬🇧 English

## 🎉 Introduction

**DevRitual** is a lightweight terminal-based ritual and habit building engine designed specifically for developers. It helps you establish and track coding habits, define daily ritual workflows, and stay motivated through beautiful statistical visualizations — all from the comfort of your terminal.

### 💡 Inspiration

As developers, we face an overwhelming amount of code and tasks every day, making it easy to fall into chaotic work rhythms. DevRitual is inspired by the concept of "ritual" — by infusing our daily development workflows with a sense of ceremony, we can build efficient and sustainable work habits. Whether it's a morning code review, a pre-commit checklist, or a daily learning streak, DevRitual helps you systematize it all.

### 🌟 Differentiation Highlights

- **Zero External Dependencies** — Built entirely with Python's standard library
- **Local-First** — All data stored in local JSON files, privacy guaranteed
- **Built-in Templates** — 8 ritual templates + 8 habit templates, ready to use
- **Heatmap Calendar** — GitHub-style activity heatmap rendered in ASCII art
- **Streak Tracking** — Automatically calculates consecutive check-in days and personal bests

## ✨ Core Features

- 🎯 **Ritual Management** — Create/edit/delete/start/complete/skip rituals with template support
- 📅 **Habit Tracking** — Daily check-ins, automatic streak calculation, personal best tracking
- 📊 **Statistics** — Daily/weekly/monthly completion rates, leaderboards, trend analysis
- 🗓️ **Heatmap Calendar** — GitHub-style activity heatmap rendered in terminal ASCII art
- 📈 **Trend Charts** — Week-over-week comparison bar charts, completion rate trend lines
- 🖥️ **TUI Dashboard** — Today's progress, to-do list, streak overview, quick stats
- 💾 **Data Management** — JSON local storage, import/export, automatic backup & restore
- 🎨 **ANSI Color Output** — Beautiful colorful terminal interface
- 📋 **Preset Templates** — 8 ritual + 8 habit templates covering common dev scenarios
- 🔒 **Privacy First** — All data stored locally, nothing uploaded to the cloud

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/DevRitual.git
cd DevRitual

# Install (development mode)
pip install -e .
```

### Getting Started

```bash
# Step 1: Initialize configuration
devritual init

# Step 2: Create a ritual from template
devritual ritual create --template morning-review

# Step 3: Create a habit
devritual habit create --name "Read tech articles daily" --frequency daily

# Step 4: Start a ritual
devritual ritual start "Morning Code Review"

# Step 5: Complete a ritual
devritual ritual complete "Morning Code Review"

# Step 6: Check in a habit
devritual habit checkin "Read tech articles daily"

# Step 7: View dashboard
devritual dashboard

# Step 8: View heatmap calendar
devritual stats calendar
```

## 📖 Detailed Usage Guide

### Ritual Management

```bash
# Create a custom ritual (interactive)
devritual ritual create

# Create from template
devritual ritual create --template morning-review
devritual ritual create --template pre-commit
devritual ritual create --template daily-standup
devritual ritual create --template weekly-retro
devritual ritual create --template code-review
devritual ritual create --template deploy-checklist
devritual ritual create --template learning-session
devritual ritual create --template end-of-day

# List all rituals
devritual ritual list

# Start a ritual
devritual ritual start "Morning Code Review"

# Complete a ritual
devritual ritual complete "Morning Code Review"

# Skip today's ritual
devritual ritual skip "Morning Code Review"

# Delete a ritual
devritual ritual delete "Morning Code Review"
```

### Habit Tracking

```bash
# Create a habit (interactive)
devritual habit create

# Quick create
devritual habit create --name "Write unit tests" --frequency daily
devritual habit create --name "Code refactoring" --frequency weekly

# List all habits
devritual habit list

# Check in
devritual habit checkin "Write unit tests"

# View streak
devritual habit streak "Write unit tests"

# Delete a habit
devritual habit delete "Write unit tests"
```

### Statistics

```bash
# View overall stats
devritual stats

# View heatmap calendar
devritual stats calendar

# View trend analysis
devritual stats trend
```

### Data Management

```bash
# Export data
devritual export

# Import data
devritual import backup.json

# View dashboard
devritual dashboard
```

## 💡 Design Philosophy & Roadmap

### Design Philosophy

DevRitual's core philosophy is **"Make good habits visible"**. By transforming the abstract process of habit building into concrete data and charts, developers can clearly see their progress trajectory and gain sustained motivation.

### Technology Choices

- **Python Standard Library** — Ensures zero dependencies, lowers installation barrier
- **JSON Storage** — Lightweight, human-readable, easy to backup and migrate
- **ANSI Escape Codes** — Colorful terminal output without extra dependencies
- **argparse** — Python's built-in CLI parsing library, stable and reliable

### Roadmap

- [ ] 🔔 Custom reminders (system notifications)
- [ ] 📊 More chart types (radar charts, pie charts)
- [ ] 🌐 Web dashboard (local HTTP server)
- [ ] 🔗 Git integration (auto-track commit habits)
- [ ] 📱 Data sync (cross-device synchronization)
- [ ] 🎮 Achievement system (unlock badges and milestones)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add some feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Submit a Pull Request

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tooling related

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
