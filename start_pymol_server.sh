#!/bin/bash

echo "=========================================="
echo "   PyMOL MCP HTTP服务器启动脚本"
echo "=========================================="
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到python3，请确保Python已安装"
    exit 1
fi

echo "[1/3] Python版本:"
python3 --version
echo

# 检查依赖
echo "[2/3] 检查依赖..."
if ! python3 -c "import mcp, starlette, uvicorn" 2>/dev/null; then
    echo "[警告] 缺少依赖，尝试安装..."
    pip3 install mcp starlette uvicorn -q || pip install mcp starlette uvicorn -q
    if [ $? -ne 0 ]; then
        echo "[错误] 安装依赖失败"
        exit 1
    fi
    echo "[OK] 依赖安装完成"
else
    echo "[OK] 依赖检查通过"
fi
echo

# 检查服务器文件
echo "[3/3] 检查服务器文件..."
if [ ! -f "pymol_mcp_server.py" ]; then
    echo "[错误] 未找到 pymol_mcp_server_http.py"
    exit 1
fi
echo "[OK] 服务器文件存在"
echo

echo "=========================================="
echo "   启动 HTTP 服务器"
echo "=========================================="
echo "[信息] 启动服务器，默认地址 http://127.0.0.1:3000"
echo "[信息] 在MCP客户端中配置URL: http://127.0.0.1:3000/sse"
echo
echo "按Ctrl+C停止服务器"
echo "=========================================="
echo

python3 pymol_mcp_server_http.py --host 127.0.0.1 --port 3000
