"""
PyMOL RPC Launcher Plugin
=========================
一键启动 XML-RPC 服务器，供 MCP 外部连接使用。

安装方法:
1. PyMOL 菜单: Plugin -> Plugin Manager -> Install New Plugin
2. 选择此文件 (pymol_rpc_launcher.py)
3. 安装后在 Plugin 菜单中点击 "Launch RPC Server" 即可

作者: pymol-ai-mcp
版本: 1.0.0
"""

import sys
import tkinter as tk
from tkinter import messagebox

def __init_plugin__(app=None):
    """插件初始化入口"""
    from pymol.plugins import addmenuitemqt
    
    def launch_rpc():
        """启动 RPC 服务器并显示弹窗"""
        start_rpc_server()
    
    # 添加菜单项
    addmenuitemqt('Launch RPC Server', launch_rpc)
    print("[RPC Plugin] Installed: Plugin -> Launch RPC Server")


def start_rpc_server():
    """启动 XML-RPC 服务器并显示提示窗口"""
    try:
        import pymol.rpc
        import xmlrpc.client
        
        # 检查 RPC 是否已经在运行
        rpc_running = False
        actual_port = None
        
        for port in range(9123, 9128):
            try:
                server = xmlrpc.client.Server(f"http://localhost:{port}", allow_none=True)
                if server.ping() == 1:
                    rpc_running = True
                    actual_port = port
                    break
            except:
                continue
        
        if rpc_running:
            # RPC 已在运行，直接显示信息
            show_info_dialog(
                "XML-RPC Server Already Running",
                f"XML-RPC server is already running!\n\n"
                f"Port: {actual_port}\n"
                f"URL: http://localhost:{actual_port}\n\n"
                f"You can now connect from external MCP clients.\n\n"
                f"Next step: Start the MCP HTTP server:\n"
                f"python pymol_mcp_server.py"
            )
        else:
            # 启动 RPC 服务器
            pymol.rpc.launch_XMLRPC()
            
            # 检测实际使用的端口
            for port in range(9123, 9128):
                try:
                    server = xmlrpc.client.Server(f"http://localhost:{port}", allow_none=True)
                    if server.ping() == 1:
                        actual_port = port
                        break
                except:
                    continue
            
            port_str = str(actual_port) if actual_port else "9123 (default)"
            
            # 显示成功弹窗
            show_info_dialog(
                "XML-RPC Server Started",
                f"XML-RPC server started successfully!\n\n"
                f"Port: {port_str}\n"
                f"URL: http://localhost:{port_str}\n\n"
                f"External control is now available.\n\n"
                f"Next step: Start the MCP HTTP server:\n"
                f"python pymol_mcp_server.py"
            )
        
        # 同时在控制台打印信息
        print("=" * 60)
        print("[RPC] XML-RPC Server is running!")
        print("=" * 60)
        print(f"[RPC] Port: {actual_port if actual_port else '9123'}")
        print(f"[RPC] URL: http://localhost:{actual_port if actual_port else '9123'}")
        print("")
        print("[MCP] Start MCP HTTP server with:")
        print("      python pymol_mcp_server.py")
        print("")
        print("[MCP] Then configure your MCP client:")
        print("      http://127.0.0.1:3000/sse")
        print("=" * 60)
        
    except ImportError as e:
        show_error_dialog("Import Error", f"Failed to import pymol.rpc:\n{e}")
    except Exception as e:
        show_error_dialog("Error", f"Failed to start RPC server:\n{e}")


def show_info_dialog(title, message):
    """显示信息弹窗"""
    try:
        # 尝试使用 PyQt (PyMOL 通常使用 PyQt)
        from PyQt5.QtWidgets import QMessageBox, QApplication
        
        # 确保有 QApplication 实例
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    except ImportError:
        # 回退到 Tkinter
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showinfo(title, message)
        root.destroy()


def show_error_dialog(title, message):
    """显示错误弹窗"""
    try:
        from PyQt5.QtWidgets import QMessageBox, QApplication
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    except ImportError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()


# 如果直接运行此文件（测试用）
if __name__ == "__main__":
    start_rpc_server()
