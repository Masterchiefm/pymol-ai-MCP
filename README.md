# PyMOL AI Controller
## 插件
MCP对于很多人来说不是那么好用，我另外做了一个ai插件，直接对话，不需要MCP等复杂调配。
https://github.com/Masterchiefm/pymol-ai-assistant

## MCP工具
通过MCP（Model Context Protocol）协议让AI控制PyMOL分子可视化软件。

本项目使用 HTTP/SSE 模式，支持远程访问和多客户端连接。

## 架构说明

```
┌─────────────┐      HTTP/SSE     ┌─────────────────┐     XML-RPC     ┌─────────┐
│  AI客户端   │  ◄────────────►  │ pymol_mcp_http  │  ◄──────────►  │  PyMOL  │
│ (网络连接)   │                  │   (HTTP服务器)   │                │         │
└─────────────┘                   └─────────────────┘                └─────────┘
       ▲
       │ HTTP/SSE
       ▼
┌─────────────┐
│  其他客户端  │
└─────────────┘
```

## 系统要求

- Python 3.10+
- PyMOL 2.0+（支持XML-RPC）

## 快速开始

### 1. 安装依赖

```bash
pip install mcp starlette uvicorn
```

或安装全部依赖：

```bash
pip install -r requirements.txt
```

### 2. 启动 HTTP 服务器

```bash
# 基本启动（默认监听 127.0.0.1:3000）
python pymol_mcp_server.py

# 指定主机和端口
python pymol_mcp_server.py --host 0.0.0.0 --port 3000

# 指定PyMOL连接参数（如果PyMOL在远程）
python pymol_mcp_server.py --pymol-host 192.168.1.100 --pymol-port 9123
```

或使用启动脚本：

```bash
# Windows
start_pymol_server.bat

# Linux/Mac
chmod +x start_pymol_server.sh
./start_pymol_server.sh
```

启动后，服务器将显示：
```
🚀 PyMOL MCP HTTP服务器已启动!
   监听地址: http://127.0.0.1:3000
   SSE端点:  http://127.0.0.1:3000/sse
   健康检查: http://127.0.0.1:3000/health
```

### 3. 在 MCP 客户端中配置 HTTP 连接

**Qwen Code - 使用命令行:**

```bash
# 添加SSE服务器
qwen mcp add --transport sse pymol http://127.0.0.1:3000/sse
```

**Qwen Code - 配置文件 (`.qwen/settings.json`):**

```json
{
  "mcpServers": {
    "pymol": {
      "url": "http://127.0.0.1:3000/sse",
      "timeout": 30000
    }
  }
}
```

**Cherry Studio - 配置文件:**

```json
{
  "mcpServers": {
    "pymol": {
      "url": "http://127.0.0.1:3000/sse"
    }
  }
}
```

**Claude Desktop - 配置文件 (`claude_desktop_config.json`):**

```json
{
  "mcpServers": {
    "pymol": {
      "url": "http://127.0.0.1:3000/sse"
    }
  }
}
```

### 4. 启动 PyMOL

```bash
pymol -R
```

或在PyMOL命令行中:
```python
import pymol.rpc
pymol.rpc.launch_XMLRPC()
```

### 5. 开始使用

现在可以直接对AI说出你的需求:

```
"从PDB获取1AKE结构"
"显示cartoon并用彩虹着色"
"缩放到蛋白质中心"
"保存为图片"
```

## 示例对话

### 示例1: 基础可视化

```
你: 帮我看看1AKE蛋白的结构

AI: 我来帮你加载并可视化1AKE蛋白。
[使用pymol_fetch获取1AKE]
[使用pymol_show显示cartoon]
[使用pymol_color彩虹着色]
[使用pymol_zoom缩放]

完成! 1AKE (Adenylate Kinase) 现在显示在PyMOL中，使用了cartoon表示和彩虹着色方案。
```

### 示例2: 配体分析

```
你: 分析1AKE的结合位点

AI: 我来分析1AKE的结合位点。
[获取结构]
[选择配体AP5]
[选择配体周围5埃的残基]
[显示配体和结合位点的sticks]
[显示蛋白质表面]

结合位点分析完成! 配体显示为sticks，周围5埃的残基也以sticks显示，
蛋白质其余部分显示为表面，可以清楚看到结合口袋。
```

### 示例3: 生成发表级图片

```
你: 生成一张高质量的1AKE图片用于论文

AI: 我来生成高质量的发表级图像。
[加载结构]
[设置白色背景]
[优化显示样式]
[光线追踪2400x2400]
[保存PNG]

高质量图像已保存! 使用了光线追踪渲染，分辨率为2400x2400像素，
适合用于论文发表。
```

## 打包成EXE（可选）

如果你想将MCP服务器打包成独立的可执行文件（无需Python环境），可以使用PyInstaller：

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 打包

**使用提供的打包脚本:**
```bash
python build_exe.py
```

**或者手动打包:**
```bash
pyinstaller --onefile --console --name pymol-mcp-server pymol_mcp_server.py --hidden-import=starlette --hidden-import=uvicorn
```

打包完成后，可执行文件位于 `dist/pymol-mcp-server.exe`。

**启动 EXE:**
```bash
pymol-mcp-server.exe --host 127.0.0.1 --port 3000
```

### 3. EXE版本的MCP配置

使用EXE文件时，MCP配置：

```json
{
  "mcpServers": {
    "pymol": {
      "url": "http://127.0.0.1:3000/sse"
    }
  }
}
```

### 4. 注意事项

- **文件大小**: 约 15-20MB（包含Starlette和Uvicorn）
- **兼容性**: 打包的EXE只能在相同操作系统架构上运行
- **杀毒软件**: 某些杀毒软件可能误报，需要添加信任
- **防火墙**: HTTP服务器需要开放相应端口，请确保防火墙允许

## 配置文件位置说明

**Qwen Code (通义灵码)** 的配置文件位置：
- **用户作用域**: `~/.qwen/settings.json` (Linux/Mac), `%USERPROFILE%\.qwen\settings.json` (Windows)
- **项目作用域**: `.qwen/settings.json` (在项目根目录下)

**Cherry Studio** 的配置文件位置：
- **Linux/Mac**: `~/.config/cherry-studio/mcp.json`
- **Windows**: `%APPDATA%\cherry-studio\mcp.json` 或 `%USERPROFILE%\.cherry-studio\mcp.json`

## 启动脚本

项目提供了便捷的启动脚本：

### Windows
```bash
start_pymol_server.bat
```

### Linux/Mac
```bash
chmod +x start_pymol_server.sh
./start_pymol_server.sh
```

脚本会自动：
- 检查Python和依赖
- 检查PyMOL MCP服务器文件
- 启动HTTP MCP服务器
- 提示需要启动PyMOL并启用XML-RPC

## 可用工具列表

| 类别 | 工具名 | 说明 |
|------|--------|------|
| 文件 | `pymol_load` | 加载本地文件 |
| 文件 | `pymol_fetch` | 从PDB获取结构 |
| 文件 | `pymol_save` | 保存结构到文件 |
| 显示 | `pymol_show` | 显示分子表示 |
| 显示 | `pymol_hide` | 隐藏分子表示 |
| 颜色 | `pymol_color` | 设置颜色 |
| 颜色 | `pymol_bg_color` | 设置背景色 |
| 视图 | `pymol_zoom` | 缩放 |
| 视图 | `pymol_orient` | 定向 |
| 视图 | `pymol_rotate` | 旋转 |
| 视图 | `pymol_reset` | 重置视图 |
| 选择 | `pymol_select` | 创建选择 |
| 选择 | `pymol_delete` | 删除对象 |
| 信息 | `pymol_get_names` | 获取对象列表 |
| 信息 | `pymol_count_atoms` | 计算原子数 |
| 信息 | `pymol_get_pdb` | 获取PDB字符串 |
| 信息 | `pymol_get_selection_info` | 获取选择的链和残基信息 |
| 渲染 | `pymol_ray` | 光线追踪 |
| 渲染 | `pymol_draw` | OpenGL渲染 |
| 渲染 | `pymol_png` | 保存PNG |
| 高级 | `pymol_do` | 执行任意命令 |

## pymol_do 命令参考

`pymol_do` 工具可以执行任意 PyMOL 命令，支持完整的命令行语法。

### 常用命令速查

#### 文件操作
```
load <file> [, <object>] [, <state>]     # 加载PDB/MOL/XYZ等文件
save <file> [, <selection>]              # 保存结构
fetch <code> [, <name>]                   # 从PDB数据库获取
delete <name>                             # 删除对象
create <name>, <selection>                # 创建新对象
```

#### 显示控制
```
show <rep> [, <selection>]    # 显示表示形式
hide <rep> [, <selection>]    # 隐藏表示形式
as <rep> [, <selection>]      # 切换表示形式

表示形式(rep): lines, sticks, spheres, surface, mesh, cartoon, ribbon, dots
```

#### 颜色控制
```
color <color> [, <selection>]   # 设置颜色
bg_color <color>                # 设置背景色
util.cbc                        # 按链着色
util.chainbow                   # 链彩虹色
util.rainbow                    # 彩虹色
util.ss                         # 二级结构着色
```

#### 预设样式
```
preset.simple <selection>          # 简单样式
preset.ball_and_stick <selection>  # 球棍模型
preset.ligands <selection>         # 配体样式
preset.pretty <selection>          # 美观样式
preset.publication <selection>     # 发表级样式
preset.technical <selection>       # 技术样式
preset.b_factor_putty <selection>  # B因子管状图
```

#### 视图控制
```
zoom <selection> [, <buffer>]   # 缩放到选择
orient <selection>              # 定向到选择
center <selection>              # 中心对齐
reset                           # 重置视图
turn <axis>, <angle>            # 旋转视图 (axis: x, y, z)
move <axis>, <distance>         # 移动视图
rock                            # 自动摇摆
```

#### 高级功能
```
ray [<width>, <height>]         # 光线追踪渲染
draw [<width>, <height>]        # OpenGL渲染
png <file> [, <w>, <h>, <dpi>]  # 保存图片
scene <name>, store             # 保存场景
scene <name>, recall            # 恢复场景
mplay                           # 播放电影
mstop                           # 停止电影
```

#### 分子操作
```
remove <selection>              # 删除原子
extract <name>, <selection>     # 提取原子
h_add <selection>               # 添加氢原子
h_remove <selection>            # 删除氢原子
remove solvent                  # 删除水分子
remove hetero                   # 删除异质原子
alter <selection>, <expr>       # 修改属性
```

#### 分析命令
```
distance <name>, <s1>, <s2>     # 测量距离
angle <name>, <s1>, <s2>, <s3>  # 测量角度
rms <sel1>, <sel2>              # 计算RMSD
align <mobile>, <target>        # 结构对齐
super <mobile>, <target>        # 高级对齐
centerofmass <selection>        # 计算质心
get_area <selection>            # 计算表面积
```

#### 选择语法示例
```
all                           # 所有原子
chain A                       # A链
resi 1-100                    # 残基1-100
resn ALA                      # 丙氨酸
name CA                       # alpha碳
elem C                        # 碳原子
organic                       # 有机配体
hetatm                        # 异质原子
sele                          # 当前选择
(chain A and resi 50-100)     # 组合条件
(all within 5 of resi 100)    # 距离选择
```

### 使用示例

```python
# 删除水分子并设置样式
pymol_do: "remove solvent; util.cbc; show cartoon"

# 高清渲染并保存
pymol_do: "bg_color white; preset.publication (all); ray 2400, 2400; png output.png"

# 分析配体结合位点
pymol_do: "select ligand, organic; select site, ligand expand 5; show sticks, ligand|site"

# 对齐结构
pymol_do: "align structure1, structure2"
```

## API端点

- **GET /sse** - SSE连接端点（客户端连接到此获取事件流）
- **POST /messages/** - 消息发送端点（客户端发送JSON-RPC消息）
- **GET /health** - 健康检查端点

## PyMOL 选择语法速查

```
all                    # 所有原子
name CA               # 所有alpha碳
resi 1-100            # 残基1-100
chain A               # A链
resn ALA              # 丙氨酸
hetatm                # 异质原子（配体、水）
organic               # 有机分子
resi 100 around 5     # 残基100周围5Å
byres (sele expand 8) # 选择周围8Å的完整残基
```

## 示例场景

### 场景1：基础蛋白质可视化

```
用户：帮我可视化Adenylate Kinase蛋白

AI：
1. 使用pymol_fetch获取1AKE结构
2. 使用pymol_show显示cartoon
3. 使用pymol_color彩虹着色
4. 使用pymol_bg_color设置白色背景
5. 使用pymol_zoom缩放
```

### 场景2：配体结合位点分析

```
用户：分析1AKE的结合位点

AI：
1. 获取1AKE结构
2. 选择配体（resn AP5）
3. 选择配体周围5Å的残基作为结合位点
4. 显示配体和结合位点的sticks
5. 显示蛋白质表面
6. 使用不同颜色区分
```

### 场景3：生成发表级图像

```
用户：生成高质量的蛋白质图像

AI：
1. 加载结构
2. 设置白色背景
3. 优化显示（cartoon + sticks）
4. 使用pymol_ray进行光线追踪
5. 使用pymol_png保存高分辨率图像
```

## 故障排除

### 问题: MCP服务器未显示

**检查:**
```bash
# Qwen Code
qwen mcp list
```

**解决:**
```bash
# 重新添加
qwen mcp remove pymol
qwen mcp add --transport sse pymol http://127.0.0.1:3000/sse
```

### 问题: 无法连接到PyMOL

**检查:**
```bash
python test_connection.py
```

**解决:**
1. 确保PyMOL启动时使用了 `-R` 参数
2. 检查PyMOL的Python控制台是否有XML-RPC启动信息
3. 确认端口9123未被占用
4. 检查防火墙设置
5. 尝试重启PyMOL

### 问题: 命令执行失败

**检查:**
- 对象名称是否正确
- 选择语法是否正确

**解决:**
使用 `pymol_do` 工具执行原始PyMOL命令进行调试。

## 开发计划

- [ ] 添加更多高级可视化功能（volume, density map等）
- [ ] 支持动画和电影生成
- [ ] 集成AI结构预测（AlphaFold等）
- [ ] 添加批量处理功能
- [ ] 支持更多文件格式

## 参考资源

- [PyMOL Wiki](https://pymolwiki.org/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [PyMOL Command Reference](https://pymolwiki.org/index.php/Category:Commands)

## License

MIT License
