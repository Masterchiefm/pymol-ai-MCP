# PyMOL AI Controller

通过MCP（Model Context Protocol）协议让AI控制PyMOL分子可视化软件。

## 架构说明

```
┌─────────────┐      MCP协议      ┌─────────────────┐     XML-RPC     ┌─────────┐
│  kimi-cli   │  ◄────────────►  │ pymol_mcp_server │  ◄──────────►  │  PyMOL  │
│  (AI客户端)  │                  │   (MCP服务器)     │                │         │
└─────────────┘                  └─────────────────┘                └─────────┘
```

## 系统要求

- Python 3.10+
- PyMOL 2.0+（支持XML-RPC）
- kimi-cli（支持MCP）

## 5分钟快速开始

### 1. 安装依赖 (1分钟)

```bash
cd pymol-ai-controller
pip install -r requirements.txt
```

### 2. 配置 MCP 服务器 (2分钟)

**方法A: 使用命令行添加（推荐）**

```bash
# Windows
kimi mcp add --transport stdio pymol -- python "C:\path\to\pymol-ai-controller\pymol_mcp_server.py"

# Linux/Mac
kimi mcp add --transport stdio pymol -- python /path/to/pymol-ai-controller/pymol_mcp_server.py
```

**方法B: 手动编辑配置文件**

编辑 `~/.kimi/mcp.json`（Windows: `%USERPROFILE%\.kimi\mcp.json`）：

```json
{
  "mcpServers": {
    "pymol": {
      "command": "python",
      "args": [
        "/path/to/pymol-ai-controller/pymol_mcp_server.py"
      ]
    }
  }
}
```

**验证配置:**
```bash
kimi mcp list
```

### 3. 启动 PyMOL (1分钟)

```bash
pymol -R
```

或在PyMOL命令行中:
```python
import pymol.rpc
pymol.rpc.launch_XMLRPC()
```

### 4. 开始使用 (无限可能)

启动 kimi-cli:
```bash
kimi
```

然后直接说出你的需求:

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

## 详细安装步骤

### 配置文件位置说明

kimi-cli的配置文件位置：
- **Linux/Mac**: `~/.config/kimi/mcp.json`
- **Windows**: `%APPDATA%\kimi\mcp.json` 或 `%USERPROFILE%\.kimi\mcp.json`

Skill目录位置：
- **Linux/Mac**: `~/.config/kimi/skills/`
- **Windows**: `%APPDATA%\kimi\skills\`

### 安装 Skill（可选）

将 `skills/pymol-control` 目录复制到 kimi-cli 的 skills 目录：

```bash
# Windows
xcopy /E /I /Y skills\pymol-control "%APPDATA%\kimi\skills\pymol-control"

# Linux/Mac
cp -r skills/pymol-control ~/.config/kimi/skills/
```

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
- 启动MCP服务器
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
| 渲染 | `pymol_ray` | 光线追踪 |
| 渲染 | `pymol_draw` | OpenGL渲染 |
| 渲染 | `pymol_png` | 保存PNG |
| 高级 | `pymol_do` | 执行任意命令 |

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
kimi mcp list
```

**解决:**
```bash
# 重新添加
kimi mcp remove pymol
kimi mcp add --transport stdio pymol -- python "完整路径\pymol_mcp_server.py"
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
