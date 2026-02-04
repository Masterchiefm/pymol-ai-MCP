# PyMOL RPC 启动器插件

一键启动 XML-RPC 服务器，方便 MCP 连接。

## 安装方法

### 方法一：直接复制（推荐）

1. 找到 PyMOL 的插件目录：
   - **Windows**: `%USERPROFILE%\pymol\plugins\`
   - **Linux/Mac**: `~/.pymol/plugins/`

2. 将 `pymol_plugin` 文件夹复制到上述目录

3. 重启 PyMOL

### 方法二：通过 PyMOL 插件管理器

1. 打开 PyMOL
2. 菜单栏：`Plugin` -> `Plugin Manager`
3. 点击 `Install New Plugin`
4. 选择 `pymol_plugin` 文件夹或打包成 zip 后选择

## 使用方法

### 方式一：点击菜单

安装后，在 PyMOL 的 `Plugin` 菜单中会看到：
```
Plugin -> 启动 RPC 服务器 (for MCP)
```

点击即可启动 XML-RPC 服务器。

### 方式二：命令行

在 PyMOL 命令行输入：
```
start_rpc
```

## 输出信息

启动成功后会显示：
```
==================================================
[RPC] XML-RPC 服务器启动成功!
==================================================
[RPC] 连接地址: http://localhost:9123
[RPC] 端口范围: 9123-9127 (自动检测)

[MCP] 启动 MCP HTTP 服务器:
      python pymol_mcp_server.py

[MCP] 然后在 MCP 客户端中配置:
      http://127.0.0.1:3000/sse
==================================================
```

## 注意事项

- 插件只会启动 XML-RPC 服务器，MCP HTTP 服务器需要单独启动
- 如果 RPC 已经在运行，插件会提示并显示连接信息
- 确保防火墙允许端口 9123-9127
