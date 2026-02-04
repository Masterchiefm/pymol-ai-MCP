"""
PyMOL RPC 启动器插件

在 PyMOL 菜单中添加一个选项，一键启动 XML-RPC 服务器
"""

import sys

def launch_rpc_plugin(app=None):
    """初始化插件，添加菜单项"""
    try:
        # 导入 PyMOL API
        from pymol import cmd
        
        # 定义启动 RPC 的函数
        def start_rpc_server():
            """启动 XML-RPC 服务器"""
            try:
                import pymol.rpc
                
                # 检查 RPC 是否已经在运行
                try:
                    # 尝试 ping 本地服务器
                    import xmlrpc.client
                    server = xmlrpc.client.Server("http://localhost:9123", allow_none=True)
                    result = server.ping()
                    if result == 1:
                        print("=" * 50)
                        print("[RPC] XML-RPC 服务器已经在运行!")
                        print("=" * 50)
                        print(f"[RPC] 连接地址: http://localhost:9123")
                        print(f"[RPC] 在 MCP 客户端中配置: http://127.0.0.1:3000/sse")
                        print("=" * 50)
                        return
                except:
                    pass  # 服务器未运行，继续启动
                
                # 启动 RPC 服务器
                pymol.rpc.launch_XMLRPC()
                
                print("=" * 50)
                print("[RPC] XML-RPC 服务器启动成功!")
                print("=" * 50)
                print(f"[RPC] 连接地址: http://localhost:9123")
                print(f"[RPC] 端口范围: 9123-9127 (自动检测)")
                print("")
                print(f"[MCP] 启动 MCP HTTP 服务器:")
                print(f"      python pymol_mcp_server.py")
                print("")
                print(f"[MCP] 然后在 MCP 客户端中配置:")
                print(f"      http://127.0.0.1:3000/sse")
                print("=" * 50)
                
            except ImportError:
                print("[错误] 无法导入 pymol.rpc，请确保 PyMOL 版本支持 RPC")
            except Exception as e:
                print(f"[错误] 启动 RPC 服务器失败: {e}")
        
        # 扩展 PyMOL 命令
        cmd.extend('start_rpc', start_rpc_server)
        
        # 添加菜单项 (如果支持)
        try:
            # 尝试添加到 Plugin 菜单
            from pymol.plugins import addmenuitemqt
            
            def menu_callback():
                start_rpc_server()
            
            addmenuitemqt('启动 RPC 服务器 (for MCP)', menu_callback)
            print("[RPC Plugin] 已加载 - 在 Plugin 菜单中找到 '启动 RPC 服务器 (for MCP)'")
            
        except Exception as e:
            # 如果无法添加菜单，至少命令是可用的
            print("[RPC Plugin] 已加载 - 在 PyMOL 命令行输入: start_rpc")
            
    except ImportError:
        print("[RPC Plugin] 错误: 无法导入 PyMOL 模块")


# 兼容直接运行
if __name__ == "__main__":
    launch_rpc_plugin()
