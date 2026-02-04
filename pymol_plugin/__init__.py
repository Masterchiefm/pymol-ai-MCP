"""
PyMOL RPC Launcher Plugin
一键启动 XML-RPC 服务器，供 MCP 连接使用
"""

def __init_plugin__(app=None):
    """插件入口点"""
    from .rpc_launcher import launch_rpc_plugin
    launch_rpc_plugin(app)
