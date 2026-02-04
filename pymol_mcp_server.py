#!/usr/bin/env python3
"""
PyMOL MCP Server - 通过MCP协议让AI控制PyMOL

这个服务器作为桥梁，将PyMOL的XML-RPC接口包装为MCP工具，
使kimi-cli或其他MCP客户端能够通过标准MCP协议控制PyMOL。

使用方法:
    1. 启动PyMOL并启用XML-RPC服务器: pymol -R
    2. 运行此服务器: python pymol_mcp_server.py
    3. 在kimi-cli中配置MCP服务器指向此服务
"""

import asyncio
import json
import sys
import xmlrpc.client
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    LoggingLevel,
)


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
            description="执行任意PyMOL命令",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "PyMOL命令字符串"
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


async def main():
    """主函数 - 启动MCP服务器"""
    # 尝试连接到PyMOL
    if not pymol_conn.connect():
        print("警告: 无法连接到PyMOL。请确保PyMOL已启动并启用了XML-RPC服务器。", file=sys.stderr)
        print("启动命令: pymol -R 或 pymol --rpc-server", file=sys.stderr)
        print("服务器将继续运行，等待PyMOL连接...", file=sys.stderr)
    
    # 使用stdio传输启动MCP服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
