#!/usr/bin/env python3
"""
PyMOL MCP Server (HTTP/SSE 版本) - 通过网络协议让AI控制PyMOL

这个服务器作为桥梁，将PyMOL的XML-RPC接口包装为MCP工具，
使kimi-cli、qwen-code或其他MCP客户端能够通过HTTP/SSE协议控制PyMOL。

使用方法:
    1. 启动PyMOL并启用XML-RPC服务器: pymol -R
    2. 运行此服务器: python pymol_mcp_server.py [--host 0.0.0.0] [--port 3000]
    3. 在MCP客户端中配置HTTP服务器指向 http://localhost:3000/sse

API端点:
    - GET /sse          - SSE连接端点（客户端连接到此获取事件流）
    - POST /messages/   - 消息发送端点（客户端发送JSON-RPC消息）
    - GET /health       - 健康检查端点
"""

import asyncio
import argparse
import json
import sys
import xmlrpc.client
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional, Any

# MCP SDK
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    LoggingLevel,
)

# HTTP服务器
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response, JSONResponse
from starlette.requests import Request
import uvicorn


@dataclass
class PyMOLConnection:
    """PyMOL XML-RPC连接管理"""
    host: str = "localhost"
    port: int = 9123
    _server: Optional[xmlrpc.client.Server] = None
    
    def connect(self) -> bool:
        """尝试连接到PyMOL XML-RPC服务器"""
        for offset in range(5):  # 尝试5个端口
            try:
                url = f"http://{self.host}:{self.port + offset}"
                self._server = xmlrpc.client.Server(url, allow_none=True)
                # 测试连接
                self._server.ping()
                print(f"已连接到PyMOL XML-RPC服务器: {url}", file=sys.stderr)
                return True
            except Exception:
                continue
        return False
    
    @property
    def server(self) -> xmlrpc.client.Server:
        if self._server is None:
            raise ConnectionError("未连接到PyMOL")
        return self._server
    
    def get_cmd(self):
        """获取cmd代理对象，可以直接调用PyMOL命令"""
        return self.server


# 全局连接实例
pymol_conn = PyMOLConnection()

# MCP服务器实例
app = Server("pymol-controller")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用的PyMOL控制工具"""
    return [
        # 文件操作
        Tool(
            name="pymol_load",
            description="从文件加载分子结构到PyMOL",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "要加载的文件路径（支持pdb, mol, cif等格式）"
                    },
                    "object_name": {
                        "type": "string",
                        "description": "对象名称（可选，默认使用文件名）"
                    },
                    "format": {
                        "type": "string",
                        "description": "文件格式（可选，自动检测）"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="pymol_fetch",
            description="从PDB数据库获取结构",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "PDB代码（如1abc）"
                    },
                    "name": {
                        "type": "string",
                        "description": "对象名称（可选）"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="pymol_save",
            description="保存当前结构到文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "保存的文件路径"
                    },
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认all）"
                    },
                    "format": {
                        "type": "string",
                        "description": "文件格式（可选）"
                    }
                },
                "required": ["filename"]
            }
        ),
        
        # 显示控制
        Tool(
            name="pymol_show",
            description="显示分子表示（representation）",
            inputSchema={
                "type": "object",
                "properties": {
                    "representation": {
                        "type": "string",
                        "description": "表示类型: lines, sticks, spheres, surface, mesh, cartoon, ribbon, dots",
                        "enum": ["lines", "sticks", "spheres", "surface", "mesh", "cartoon", "ribbon", "dots", "nonbonded", "nb_spheres"]
                    },
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认all）"
                    }
                },
                "required": ["representation"]
            }
        ),
        Tool(
            name="pymol_hide",
            description="隐藏分子表示",
            inputSchema={
                "type": "object",
                "properties": {
                    "representation": {
                        "type": "string",
                        "description": "表示类型（默认all）"
                    },
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认all）"
                    }
                }
            }
        ),
        
        # 颜色控制
        Tool(
            name="pymol_color",
            description="设置对象颜色",
            inputSchema={
                "type": "object",
                "properties": {
                    "color": {
                        "type": "string",
                        "description": "颜色名称或颜色值（如red, blue, green, rainbow, cpk等）"
                    },
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认all）"
                    }
                },
                "required": ["color"]
            }
        ),
        Tool(
            name="pymol_bg_color",
            description="设置背景颜色",
            inputSchema={
                "type": "object",
                "properties": {
                    "color": {
                        "type": "string",
                        "description": "颜色名称（如white, black, gray）"
                    }
                },
                "required": ["color"]
            }
        ),
        
        # 视图控制
        Tool(
            name="pymol_zoom",
            description="缩放到选择区域",
            inputSchema={
                "type": "object",
                "properties": {
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认all）"
                    },
                    "buffer": {
                        "type": "number",
                        "description": "缓冲区大小"
                    }
                }
            }
        ),
        Tool(
            name="pymol_orient",
            description="定向到选择区域",
            inputSchema={
                "type": "object",
                "properties": {
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认all）"
                    }
                }
            }
        ),
        Tool(
            name="pymol_rotate",
            description="旋转视图或对象",
            inputSchema={
                "type": "object",
                "properties": {
                    "axis": {
                        "type": "string",
                        "description": "旋转轴: x, y, z",
                        "enum": ["x", "y", "z"]
                    },
                    "angle": {
                        "type": "number",
                        "description": "旋转角度（度）"
                    },
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认空，表示旋转视图）"
                    }
                },
                "required": ["axis", "angle"]
            }
        ),
        Tool(
            name="pymol_reset",
            description="重置视图",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # 选择操作
        Tool(
            name="pymol_select",
            description="创建选择",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "选择名称"
                    },
                    "expression": {
                        "type": "string",
                        "description": "选择表达式（如chain A, resi 1-100, name CA）"
                    }
                },
                "required": ["name", "expression"]
            }
        ),
        Tool(
            name="pymol_delete",
            description="删除对象或选择",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "对象或选择名称"
                    }
                },
                "required": ["name"]
            }
        ),
        
        # 获取信息
        Tool(
            name="pymol_get_names",
            description="获取所有对象名称",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "类型: objects, selections, all",
                        "enum": ["objects", "selections", "all"]
                    }
                }
            }
        ),
        Tool(
            name="pymol_count_atoms",
            description="计算原子数量",
            inputSchema={
                "type": "object",
                "properties": {
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认all）"
                    }
                }
            }
        ),
        Tool(
            name="pymol_get_pdb",
            description="获取PDB格式字符串",
            inputSchema={
                "type": "object",
                "properties": {
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认all）"
                    }
                }
            }
        ),
        Tool(
            name="pymol_get_selection_info",
            description="获取选择中的链和残基信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "selection": {
                        "type": "string",
                        "description": "选择表达式（默认为 'sele'）"
                    }
                }
            }
        ),

        # 高级功能
        Tool(
            name="pymol_ray",
            description="光线追踪渲染",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {
                        "type": "integer",
                        "description": "宽度（像素）"
                    },
                    "height": {
                        "type": "integer",
                        "description": "高度（像素）"
                    }
                }
            }
        ),
        Tool(
            name="pymol_draw",
            description="绘制当前视图（使用OpenGL）",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {
                        "type": "integer",
                        "description": "宽度"
                    },
                    "height": {
                        "type": "integer",
                        "description": "高度"
                    }
                }
            }
        ),
        Tool(
            name="pymol_png",
            description="保存当前视图为PNG",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "PNG文件路径"
                    },
                    "width": {
                        "type": "integer",
                        "description": "宽度"
                    },
                    "height": {
                        "type": "integer",
                        "description": "高度"
                    },
                    "dpi": {
                        "type": "integer",
                        "description": "DPI"
                    },
                    "ray": {
                        "type": "boolean",
                        "description": "是否先进行光线追踪"
                    }
                },
                "required": ["filename"]
            }
        ),
        
        # 执行任意命令
        Tool(
            name="pymol_do",
            description="""执行任意PyMOL命令，如Python的cmd.do()。支持所有PyMOL命令行指令。

常用命令类别：

【文件操作】
- load <file> [, <object>] [, <state>] - 加载PDB/MOL/XYZ等文件
- save <file> [, <selection>] [, <state>] [, <format>] - 保存结构
- fetch <code> [, <name>] [, <state>] - 从PDB数据库获取
- delete <name> - 删除对象
- create <name>, <selection> [, <source_state>] [, <target_state>] - 创建新对象

【显示控制】
- show <representation> [, <selection>] - 显示表示形式
- hide <representation> [, <selection>] - 隐藏表示形式
- as <representation> [, <selection>] - 切换表示形式
- representation: lines, sticks, spheres, surface, mesh, cartoon, ribbon, dots, nonbonded, nb_spheres

【颜色控制】
- color <color> [, <selection>] - 设置颜色
- bg_color <color> - 设置背景色
- util.cbc - 按链着色 (color by chain)
- util.chainbow - 链彩虹色
- util.rainbow - 彩虹色
- util.ss - 二级结构着色
- color gray, (elem C) - 碳原子灰色

【预设样式】
- preset.simple <selection> - 简单样式
- preset.ball_and_stick <selection> - 球棍模型
- preset.ligands <selection> - 配体样式
- preset.pretty <selection> - 美观样式
- preset.publication <selection> - 发表级样式
- preset.technical <selection> - 技术样式
- preset.b_factor_putty <selection> - B因子管状图

【视图控制】
- zoom <selection> [, <buffer>] - 缩放到选择
- orient <selection> - 定向到选择
- center <selection> - 中心对齐
- reset - 重置视图
- turn <axis>, <angle> - 旋转视图
- move <axis>, <distance> - 移动视图
- rock - 自动摇摆
- rock <frames> - 摇摆指定帧数

【选择操作】
- select <name>, <selection> - 创建选择
- deselect - 取消选择
- enable <name> - 启用对象
- disable <name> - 禁用对象

【高级功能】
- ray [<width>], [<height>] - 光线追踪渲染
- draw [<width>], [<height>] - OpenGL渲染
- png <filename> [, <width>], [<height>], [<dpi>], [<ray>] - 保存图片
- mpng <prefix> [, <first>], [<last>] - 保存多帧图片
- scene <name>, <action> - 场景管理 (store/recall/clear)
- view <name>, <action> - 视图管理
- mset <spec> - 设置电影帧
- mplay - 播放电影
- mstop - 停止电影

【分子操作】
- remove <selection> - 删除原子
- extract <name>, <selection> - 提取原子
- h_add <selection> - 添加氢原子
- h_remove <selection> - 删除氢原子
- remove solvent - 删除水分子
- alter <selection>, <expression> - 修改属性
- iterate <selection>, <expression> - 遍历原子

【分析】
- distance <name>, <selection1>, <selection2> - 测量距离
- angle <name>, <s1>, <s2>, <s3> - 测量角度
- dihedral <name>, <s1>, <s2>, <s3>, <s4> - 测量二面角
- rms <selection1>, <selection2> - 计算RMSD
- align <mobile>, <target> - 结构对齐
- super <mobile>, <target> - 高级对齐
- centerofmass <selection> - 计算质心
- get_area <selection> - 计算表面积

【外观设置】
- set <setting>, <value> [, <selection>] - 设置参数
- cartoon <type> - 卡通类型 (skip/loop/rectangle/oval/tube)
- set_bond <setting>, <value>, <selection1>, <selection2>
- set_view (...) - 设置视图矩阵

【选择语法示例】
- all - 所有原子
- chain A - A链
- resi 1-100 - 残基1-100
- resn ALA - 丙氨酸
- name CA - alpha碳
- elem C - 碳原子
- organic - 有机配体
- hetatm - 异质原子
- solvent - 溶剂/水
- (chain A and resi 50-100) - 组合条件
- (all within 5 of resi 100) - 距离选择

使用示例：
- "remove solvent" - 删除水分子
- "color marine, chain A" - A链设为海蓝色
- "show sticks, organic" - 显示配体为棍状
- "preset.pretty (all)" - 应用美观预设
- "ray 2400, 2400" - 高清光线追踪
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "PyMOL命令字符串，支持完整的PyMOL命令语法。可以是单条命令或多条命令用分号分隔。例如: 'remove solvent; color marine, chain A; show sticks, organic'"
                    }
                },
                "required": ["command"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    if pymol_conn._server is None:
        return [TextContent(type="text", text="错误: 未连接到PyMOL。请确保PyMOL已启动并启用了XML-RPC服务器（pymol -R）")]
    
    try:
        cmd = pymol_conn.get_cmd()
        
        # 文件操作
        if name == "pymol_load":
            filename = arguments["filename"]
            obj_name = arguments.get("object_name", "")
            fmt = arguments.get("format", "")
            result = cmd.load(filename, obj_name, format=fmt)
            return [TextContent(type="text", text=f"已加载文件: {filename}, 对象名称: {result}")]
        
        elif name == "pymol_fetch":
            code = arguments["code"]
            name = arguments.get("name", "")
            result = cmd.fetch(code, name)
            return [TextContent(type="text", text=f"已从PDB获取: {code}")]
        
        elif name == "pymol_save":
            filename = arguments["filename"]
            selection = arguments.get("selection", "(all)")
            fmt = arguments.get("format", "")
            cmd.save(filename, selection, format=fmt)
            return [TextContent(type="text", text=f"已保存到: {filename}")]
        
        # 显示控制
        elif name == "pymol_show":
            rep = arguments["representation"]
            selection = arguments.get("selection", "all")
            cmd.show(rep, selection)
            return [TextContent(type="text", text=f"已显示 {rep} for {selection}")]
        
        elif name == "pymol_hide":
            rep = arguments.get("representation", "all")
            selection = arguments.get("selection", "all")
            cmd.hide(rep, selection)
            return [TextContent(type="text", text=f"已隐藏 {rep} for {selection}")]
        
        # 颜色控制
        elif name == "pymol_color":
            color = arguments["color"]
            selection = arguments.get("selection", "all")
            cmd.color(color, selection)
            return [TextContent(type="text", text=f"已将 {selection} 设置为 {color} 颜色")]
        
        elif name == "pymol_bg_color":
            color = arguments["color"]
            cmd.bg_color(color)
            return [TextContent(type="text", text=f"已设置背景颜色为: {color}")]
        
        # 视图控制
        elif name == "pymol_zoom":
            selection = arguments.get("selection", "all")
            buffer = arguments.get("buffer", 0.0)
            cmd.zoom(selection, buffer)
            return [TextContent(type="text", text=f"已缩放到: {selection}")]
        
        elif name == "pymol_orient":
            selection = arguments.get("selection", "all")
            cmd.orient(selection)
            return [TextContent(type="text", text=f"已定向到: {selection}")]
        
        elif name == "pymol_rotate":
            axis = arguments["axis"]
            angle = arguments["angle"]
            selection = arguments.get("selection", "")
            if selection:
                cmd.rotate(axis, angle, selection)
                return [TextContent(type="text", text=f"已旋转 {selection} 沿 {axis} 轴 {angle}度")]
            else:
                cmd.turn(axis, angle)
                return [TextContent(type="text", text=f"已旋转视图 沿 {axis} 轴 {angle}度")]
        
        elif name == "pymol_reset":
            cmd.reset()
            return [TextContent(type="text", text="已重置视图")]
        
        # 选择操作
        elif name == "pymol_select":
            sel_name = arguments["name"]
            expression = arguments["expression"]
            cmd.select(sel_name, expression)
            return [TextContent(type="text", text=f"已创建选择 '{sel_name}': {expression}")]
        
        elif name == "pymol_delete":
            name = arguments["name"]
            cmd.delete(name)
            return [TextContent(type="text", text=f"已删除: {name}")]
        
        # 获取信息
        elif name == "pymol_get_names":
            type_ = arguments.get("type", "objects")
            names = cmd.get_names(type_, enabled_only=1)
            return [TextContent(type="text", text=f"{type_}: {', '.join(names)}")]
        
        elif name == "pymol_count_atoms":
            selection = arguments.get("selection", "all")
            count = cmd.count_atoms(selection)
            return [TextContent(type="text", text=f"{selection} 中的原子数: {count}")]
        
        elif name == "pymol_get_pdb":
            selection = arguments.get("selection", "all")
            pdb_str = cmd.get_pdbstr(selection)
            return [TextContent(type="text", text=f"PDB格式:\n```\n{pdb_str[:2000]}\n```")]

        elif name == "pymol_get_selection_info":
            """
            获取选择中的链和残基信息

            判断方法：
            1. 获取选择的总原子数（使用 cmd.count_atoms）
            2. 遍历所有可能的链标识符（A-Z），测试每个链在选择中的原子数
            3. 获取 PDB 格式文本，解析出每个原子的链标识符和残基信息
            4. 返回包含的链列表、每条链的原子数和残基范围
            """
            selection = arguments.get("selection", "sele")

            # 获取总原子数
            total_atoms = cmd.count_atoms(selection)

            if total_atoms == 0:
                return [TextContent(type="text", text=f"选择 '{selection}' 为空，没有选中任何原子")]

            # 遍历所有可能的链标识符，收集链信息
            chains_info = {}
            possible_chains = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            for chain_id in possible_chains:
                chain_count = cmd.count_atoms(f"({selection}) and chain {chain_id}")
                if chain_count > 0:
                    chains_info[chain_id] = {"atom_count": chain_count}

            # 获取 PDB 文本，提取残基信息
            pdb_str = cmd.get_pdbstr(selection)
            lines = pdb_str.split("\n")

            # 解析每个原子的信息
            for line in lines:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    # PDB 格式：链标识符在第 21 列（索引 21，从 0 开始）
                    if len(line) > 21:
                        chain_id = line[21]
                        # 残基编号从第 22-26 列
                        resi_str = line[22:26].strip()
                        # 残基名称从第 17-20 列
                        resn = line[17:20].strip()

                        if chain_id in chains_info:
                            if "residues" not in chains_info[chain_id]:
                                chains_info[chain_id]["residues"] = []
                            try:
                                resi_num = int(resi_str)
                                chains_info[chain_id]["residues"].append({
                                    "resi": resi_num,
                                    "resn": resn
                                })
                            except ValueError:
                                pass

            # 整理残基范围
            result_text = f"选择 '{selection}' 信息：\n"
            result_text += f"总原子数: {total_atoms}\n"
            result_text += "包含的链:\n"

            for chain_id, info in chains_info.items():
                result_text += f"  链 {chain_id}: {info['atom_count']} 个原子"
                if "residues" in info and info["residues"]:
                    residues = info["residues"]
                    residues.sort(key=lambda x: x["resi"])
                    unique_resi = list({r["resi"] for r in residues})
                    if unique_resi:
                        min_resi = min(unique_resi)
                        max_resi = max(unique_resi)
                        if min_resi == max_resi:
                            result_text += f", 残基 {min_resi} ({residues[0]['resn']})"
                        else:
                            result_text += f", 残基 {min_resi}-{max_resi}"
                result_text += "\n"

            return [TextContent(type="text", text=result_text)]

        # 高级功能
        elif name == "pymol_ray":
            width = arguments.get("width", 0)
            height = arguments.get("height", 0)
            cmd.ray(width, height)
            return [TextContent(type="text", text=f"已完成光线追踪渲染 ({width}x{height})")]
        
        elif name == "pymol_draw":
            width = arguments.get("width", 0)
            height = arguments.get("height", 0)
            cmd.draw(width, height)
            return [TextContent(type="text", text=f"已绘制视图 ({width}x{height})")]
        
        elif name == "pymol_png":
            filename = arguments["filename"]
            width = arguments.get("width", 0)
            height = arguments.get("height", 0)
            dpi = arguments.get("dpi", -1)
            ray = arguments.get("ray", False)
            cmd.png(filename, width, height, dpi=dpi, ray=int(ray))
            return [TextContent(type="text", text=f"已保存PNG: {filename}")]
        
        # 执行任意命令
        elif name == "pymol_do":
            command = arguments["command"]
            result = cmd.do(command)
            return [TextContent(type="text", text=f"执行命令: {command}\n结果: {result}")]
        
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]


def create_starlette_app(mcp_server: Server, sse_transport: SseServerTransport) -> Starlette:
    """创建Starlette应用"""
    
    async def handle_sse(request: Request):
        """处理SSE连接请求"""
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )
        return Response()
    
    async def health_check(request: Request):
        """健康检查端点"""
        return JSONResponse({
            "status": "ok",
            "pymol_connected": pymol_conn._server is not None,
            "server": "pymol-controller"
        })
    
    async def root(request: Request):
        """根路径 - 显示服务器信息"""
        return JSONResponse({
            "name": "PyMOL MCP Server",
            "version": "1.0.0",
            "endpoints": {
                "/sse": "SSE连接端点 (用于MCP客户端连接)",
                "/messages/": "消息发送端点 (POST请求)",
                "/health": "健康检查端点"
            },
            "transport": "sse",
            "pymol_connected": pymol_conn._server is not None
        })
    
    routes = [
        Route("/", endpoint=root, methods=["GET"]),
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Route("/health", endpoint=health_check, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]
    
    return Starlette(routes=routes)


async def main():
    """主函数 - 启动HTTP MCP服务器"""
    parser = argparse.ArgumentParser(description="PyMOL MCP HTTP服务器")
    parser.add_argument("--host", default="127.0.0.1", help="绑定地址 (默认: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=3000, help="监听端口 (默认: 3000)")
    parser.add_argument("--pymol-host", default="localhost", help="PyMOL XML-RPC主机")
    parser.add_argument("--pymol-port", type=int, default=9123, help="PyMOL XML-RPC端口")
    args = parser.parse_args()
    
    # 配置PyMOL连接
    pymol_conn.host = args.pymol_host
    pymol_conn.port = args.pymol_port
    
    # 尝试连接到PyMOL
    if not pymol_conn.connect():
        print("警告: 无法连接到PyMOL。请确保PyMOL已启动并启用了XML-RPC服务器。", file=sys.stderr)
        print("启动命令: pymol -R 或 pymol --rpc-server", file=sys.stderr)
        print("服务器将继续运行，等待PyMOL连接...", file=sys.stderr)
    
    # 创建SSE传输
    sse = SseServerTransport("/messages/")
    
    # 创建Starlette应用
    starlette_app = create_starlette_app(app, sse)
    
    print(f"\n🚀 PyMOL MCP HTTP服务器已启动!")
    print(f"   监听地址: http://{args.host}:{args.port}")
    print(f"   SSE端点:  http://{args.host}:{args.port}/sse")
    print(f"   健康检查: http://{args.host}:{args.port}/health")
    print(f"\n在MCP客户端中使用此URL配置: http://{args.host}:{args.port}/sse")
    print("")
    
    # 启动Uvicorn服务器
    config = uvicorn.Config(starlette_app, host=args.host, port=args.port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
