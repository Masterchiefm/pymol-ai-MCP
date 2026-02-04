#!/usr/bin/env python3
"""
测试 PyMOL XML-RPC 连接

使用方法:
    1. 确保PyMOL已启动: pymol -R
    2. 运行此脚本: python test_connection.py
"""

import sys
import xmlrpc.client


def test_pymol_connection(host="localhost", start_port=9123, max_attempts=5):
    """测试PyMOL XML-RPC连接"""
    print("=" * 50)
    print("PyMOL XML-RPC 连接测试")
    print("=" * 50)
    
    server = None
    connected_port = None
    
    # 尝试连接
    for offset in range(max_attempts):
        port = start_port + offset
        try:
            url = f"http://{host}:{port}"
            print(f"\n尝试连接到: {url}")
            server = xmlrpc.client.Server(url, allow_none=True)
            
            # 测试ping
            result = server.ping()
            if result == 1:
                print(f"✓ 连接成功!")
                connected_port = port
                break
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            continue
    
    if server is None:
        print("\n" + "=" * 50)
        print("错误: 无法连接到PyMOL")
        print("=" * 50)
        print("\n请确保:")
        print("1. PyMOL已启动")
        print("2. PyMOL启用了XML-RPC服务器 (启动时添加 -R 参数)")
        print("   命令: pymol -R")
        print("3. 防火墙未阻止端口 9123-9127")
        return False
    
    # 测试基本功能
    print("\n" + "=" * 50)
    print("测试基本功能")
    print("=" * 50)
    
    try:
        # 测试获取对象列表
        print("\n1. 获取对象列表...")
        names = server.get_names("objects", 1)
        print(f"   当前对象: {names if names else '(无)'}")
        
        # 测试获取选择列表
        print("\n2. 获取选择列表...")
        selections = server.get_names("selections", 1)
        print(f"   当前选择: {selections if selections else '(无)'}")
        
        # 测试计数
        print("\n3. 计算原子数...")
        count = server.count_atoms("all")
        print(f"   总原子数: {count}")
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过!")
        print("=" * 50)
        print(f"\nPyMOL XML-RPC 服务器运行在端口: {connected_port}")
        return True
        
    except Exception as e:
        print(f"\n✗ 功能测试失败: {e}")
        return False


if __name__ == "__main__":
    success = test_pymol_connection()
    sys.exit(0 if success else 1)
