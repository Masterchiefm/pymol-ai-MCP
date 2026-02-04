# PyMOL RPC Launcher Plugin

一键启动 XML-RPC 服务器的 PyMOL 插件，方便 MCP 外部连接。

## 安装步骤

### 1. 打开 PyMOL Plugin Manager

菜单栏: `Plugin` -> `Plugin Manager`

![Step 1](https://i.imgur.com/placeholder1.png)

### 2. 安装插件

在 Plugin Manager 窗口中:
1. 点击 `Install New Plugin` 标签
2. 点击 `Choose file...` 按钮
3. 选择 `pymol_rpc_launcher.py` 文件
4. 点击 `Open` 安装

![Step 2](https://i.imgur.com/placeholder2.png)

### 3. 完成安装

安装成功后，会在 `Plugin` 菜单中看到 `Launch RPC Server` 选项。

## 使用方法

### 启动 RPC 服务器

1. 点击菜单: `Plugin` -> `Launch RPC Server`

2. 弹出窗口显示启动信息:
   ```
   XML-RPC Server Started
   
   XML-RPC server started successfully!
   
   Port: 9123
   URL: http://localhost:9123
   
   External control is now available.
   
   Next step: Start the MCP HTTP server:
   python pymol_mcp_server.py
   ```

3. 点击 `OK` 关闭提示窗口

### 如果 RPC 已在运行

插件会检测到已有的 RPC 服务器，并显示:
```
XML-RPC Server Already Running

XML-RPC server is already running!

Port: 9123
URL: http://localhost:9123
...
```

## 完整工作流程

```
1. 打开 PyMOL
      ↓
2. Plugin -> Launch RPC Server
      ↓
3. 看到弹窗 "XML-RPC Server Started"
      ↓
4. 点击 OK 关闭弹窗
      ↓
5. 在终端启动 MCP HTTP 服务器:
   python pymol_mcp_server.py
      ↓
6. 在 MCP 客户端中配置连接
```

## 功能特点

- ✅ 单个 .py 文件，Plugin Manager 直接安装
- ✅ 点击菜单即可启动
- ✅ 弹窗提示，清晰直观
- ✅ 自动检测端口
- ✅ 防止重复启动
- ✅ 控制台同时输出详细信息

## 故障排除

### 插件安装后菜单不显示
- 重启 PyMOL
- 检查 Plugin Manager 中是否已列出该插件

### 启动失败
- 确保 PyMOL 版本支持 RPC (PyMOL 2.0+)
- 检查端口 9123-9127 是否被占用

### 弹窗无法显示
- 插件会自动尝试 PyQt5 或 Tkinter
- 确保 PyMOL 有 GUI 环境（非命令行模式）
