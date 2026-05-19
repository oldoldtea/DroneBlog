---
title: Tauri 跨平台桌面应用开发指南
date: 2026-05-18 17:27:23
tags:
  - Tauri
  - 桌面应用
categories:
  - 前端技术
---

## 引言

在桌面应用开发领域，[Tauri](https://tauri.app/) 正迅速成为一个备受瞩目的选择。它允许开发者使用 Web 前端技术（HTML、CSS、JavaScript/TypeScript）构建用户界面，同时以 Rust 编写后端逻辑，最终打包出体积小巧、性能优异的跨平台桌面应用。与 Electron 相比，Tauri 的应用体积可缩小数十倍，且内存占用更低。

<!-- more -->

## Tauri 是什么

Tauri 是一个用于构建跨平台桌面应用的框架，其核心设计理念是：

- **前端自由**：使用任何前端框架（React、Vue、Svelte、Vanilla JS 等）构建 UI
- **Rust 后端**：利用 Rust 的安全性和性能处理系统级操作
- **极小体积**：最终二进制文件通常只有几 MB，远小于 Electron 应用的数百 MB
- **安全优先**：默认启用多种安全策略，如内容安全策略（CSP）、进程隔离等

## 环境准备

在开始之前，需要安装以下依赖：

### 1. Rust 工具链

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

安装完成后，重启终端并验证：

```bash
rustc --version
cargo --version
```

### 2. 系统依赖

**macOS / Linux：**

```bash
# macOS
xcode-select --install

# Debian/Ubuntu
sudo apt update
sudo apt install libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev
```

**Windows：**

需要安装 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)，选择"使用 C++ 的桌面开发"工作负载。

### 3. Node.js 与前端工具

```bash
# 安装 Node.js（建议 v18+）
node --version  # v18.0.0 或更高

# 安装 Tauri CLI
npm install -g @tauri-apps/cli
```

## 创建第一个 Tauri 项目

### 使用 create-tauri-app

最快捷的方式是使用官方脚手架：

```bash
npm create tauri-app@latest
```

按提示选择：
- 项目名称：`my-tauri-app`
- 前端语言：TypeScript / JavaScript
- 包管理器：npm
- UI 模板：Vanilla / Vue / React / Svelte 等

### 项目结构

创建完成后，项目目录结构如下：

```
my-tauri-app/
├── src/                  # 前端源码
│   ├── main.ts
│   └── index.html
├── src-tauri/            # Rust 后端源码
│   ├── Cargo.toml        # Rust 依赖配置
│   ├── tauri.conf.json   # Tauri 配置
│   ├── icons/            # 应用图标
│   └── src/
│       └── main.rs       # 入口文件
├── package.json
└── vite.config.ts
```

### 运行项目

```bash
cd my-tauri-app
npm install
npm run tauri dev
```

首次编译 Rust 代码可能需要几分钟，后续会快很多。运行成功后会弹出一个桌面窗口，加载你的前端页面。

## 核心概念：前端与后端的通信

Tauri 的核心能力在于前端 JavaScript 与后端 Rust 之间的安全通信，主要通过两种方式实现：

### 1. Commands（命令）

前端调用 Rust 函数并获取返回值。

**Rust 端定义（`src-tauri/src/main.rs`）：**

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

// 定义一个 Tauri Command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("你好，{}！这是来自 Rust 的问候。", name)
}

// 异步 Command
#[tauri::command]
async fn fetch_data(url: &str) -> Result<String, String> {
    let response = reqwest::get(url)
        .await
        .map_err(|e| e.to_string())?
        .text()
        .await
        .map_err(|e| e.to_string())?;
    Ok(response)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet, fetch_data])
        .run(tauri::generate_context!())
        .expect("运行 Tauri 应用时出错");
}
```

**前端调用（JavaScript/TypeScript）：**

```typescript
import { invoke } from '@tauri-apps/api/tauri';

// 调用同步 Command
async function sayHello() {
  const result = await invoke('greet', { name: 'Tauri' });
  console.log(result); // 输出：你好，Tauri！这是来自 Rust 的问候。
}

// 调用异步 Command
async function loadData() {
  try {
    const data = await invoke('fetch_data', { url: 'https://api.example.com/data' });
    console.log(data);
  } catch (error) {
    console.error('请求失败:', error);
  }
}
```

### 2. Events（事件）

用于单向广播或前端/后端主动推送消息。

**Rust 端发送事件：**

```rust
use tauri::Manager;

// 在应用启动后发送事件
fn setup_app(app: &mut tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    let window = app.get_window("main").unwrap();
    window.emit("backend-event", "后端已就绪")?;
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .setup(setup_app)
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**前端监听事件：**

```typescript
import { listen } from '@tauri-apps/api/event';

const unlisten = await listen('backend-event', (event) => {
  console.log('收到后端消息:', event.payload);
});

// 组件卸载时取消监听
// unlisten();
```

## 常用系统 API

Tauri 提供了丰富的 JavaScript API 来访问系统功能：

### 文件系统操作

```typescript
import { readTextFile, writeTextFile, BaseDirectory } from '@tauri-apps/api/fs';

// 读取应用配置目录下的文件
const content = await readTextFile('config.json', { dir: BaseDirectory.AppConfig });

// 写入文件
await writeTextFile('notes.txt', 'Hello Tauri!', { dir: BaseDirectory.Document });
```

### 对话框

```typescript
import { open, save } from '@tauri-apps/api/dialog';

// 打开文件选择对话框
const selected = await open({
  multiple: false,
  filters: [{
    name: '图片',
    extensions: ['png', 'jpg', 'jpeg']
  }]
});

// 保存文件对话框
const filePath = await save({
  filters: [{
    name: '文本文件',
    extensions: ['txt']
  }]
});
```

### 系统通知

```typescript
import { isPermissionGranted, requestPermission, sendNotification } from '@tauri-apps/api/notification';

let permissionGranted = await isPermissionGranted();
if (!permissionGranted) {
  const permission = await requestPermission();
  permissionGranted = permission === 'granted';
}

if (permissionGranted) {
  sendNotification({ title: 'Tauri', body: '任务已完成！' });
}
```

### 剪贴板

```typescript
import { writeText, readText } from '@tauri-apps/api/clipboard';

await writeText('复制到剪贴板的内容');
const text = await readText();
```

## 打包与发布

### 配置应用信息

编辑 `src-tauri/tauri.conf.json`：

```json
{
  "tauri": {
    "bundle": {
      "identifier": "com.example.myapp",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/icon.ico"
      ],
      "category": "DeveloperTool",
      "shortDescription": "我的 Tauri 应用",
      "longDescription": "这是一个使用 Tauri 构建的跨平台桌面应用"
    }
  }
}
```

### 构建发布版本

```bash
npm run tauri build
```

构建完成后，安装包位于：

- **macOS**：`src-tauri/target/release/bundle/dmg/*.dmg`
- **Windows**：`src-tauri/target/release/bundle/msi/*.msi`
- **Linux**：`src-tauri/target/release/bundle/deb/*.deb`

### 跨平台编译

Tauri 支持 GitHub Actions 自动构建多平台安装包。在项目根目录创建 `.github/workflows/release.yml`：

```yaml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        platform: [macos-latest, ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.platform }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - uses: dtolnay/rust-action@stable
      - run: npm install
      - run: npm run tauri build
      - uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Tauri vs Electron

| 特性 | Tauri | Electron |
|------|-------|----------|
| 应用体积 | ~3-6 MB | ~150-300 MB |
| 内存占用 | 较低 | 较高 |
| 前端技术 | 任意框架 | 任意框架 |
| 后端语言 | Rust | Node.js |
| 安全性 | 默认严格 | 需手动配置 |
| 系统 API | Rust 原生 + JS API | Node.js API |
| 打包速度 | 较慢（Rust 编译） | 较快 |
| 生态成熟度 | 快速发展中 | 非常成熟 |

## 最佳实践

1. **最小权限原则**：在 `tauri.conf.json` 中仅启用需要的 API，禁用未使用的功能
2. **前端状态管理**：复杂应用建议使用 Pinia/Vuex（Vue）或 Redux/Zustand（React）
3. **错误处理**：Rust 函数返回 `Result<T, String>`，前端做好错误捕获
4. **类型安全**：使用 TypeScript 并定义 Command 的输入输出类型
5. **性能优化**：大文件操作、复杂计算放在 Rust 端执行

## 总结

Tauri 为桌面应用开发提供了一个现代化、高性能的选择。它结合了 Web 技术的开发效率和 Rust 的系统级能力，同时解决了 Electron 体积臃肿的问题。对于追求小巧、安全、跨平台的桌面应用开发者来说，Tauri 值得深入学习和使用。

## 参考资源

- [Tauri 官方文档](https://tauri.app/v1/guides/)
- [Tauri API 参考](https://tauri.app/v1/api/js/)
- [Awesome Tauri](https://github.com/tauri-apps/awesome-tauri)
- [Tauri GitHub 仓库](https://github.com/tauri-apps/tauri)
