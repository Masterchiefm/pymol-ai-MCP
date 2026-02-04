#!/usr/bin/env python3
"""
打包 PyMOL MCP HTTP Server 为可执行文件
"""

import PyInstaller.__main__
import os
import sys

def build_exe():
    """使用PyInstaller打包HTTP版本"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(current_dir, "pymol_mcp_server.py")
    
    args = [
        server_script,
        '--name=pymol-mcp-server',
        '--onefile',
        '--console',
        '--clean',
        '--noconfirm',
        # 隐藏导入的模块
        '--hidden-import=mcp.server',
        '--hidden-import=mcp.server.sse',
        '--hidden-import=mcp.types',
        '--hidden-import=starlette',
        '--hidden-import=starlette.applications',
        '--hidden-import=starlette.routing',
        '--hidden-import=starlette.responses',
        '--hidden-import=starlette.requests',
        '--hidden-import=uvicorn',
    ]
    
    print(f"正在打包: {server_script}")
    print(f"参数: {args}")
    
    PyInstaller.__main__.run(args)
    
    print("\n打包完成!")
    print(f"输出目录: {os.path.join(current_dir, 'dist')}")
    print(f"可执行文件: {os.path.join(current_dir, 'dist', 'pymol-mcp-server.exe')}")
    print("\n使用方法:")
    print("  pymol-mcp-server.exe --host 127.0.0.1 --port 3000")
    print("\n在MCP客户端中配置URL:")
    print("  http://127.0.0.1:3000/sse")

if __name__ == "__main__":
    try:
        import PyInstaller
    except ImportError:
        print("请先安装 PyInstaller:")
        print("  pip install pyinstaller")
        sys.exit(1)
    
    build_exe()
