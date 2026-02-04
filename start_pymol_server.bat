@echo off
chcp 65001 >nul
echo ==========================================
echo    PyMOL MCP HTTP服务器启动脚本
echo ==========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo [1/3] Python版本:
python --version
echo.

REM 检查依赖
echo [2/3] 检查依赖...
python -c "import mcp, starlette, uvicorn" 2>nul
if errorlevel 1 (
    echo [警告] 缺少依赖，尝试安装...
    pip install mcp starlette uvicorn -q
    if errorlevel 1 (
        echo [错误] 安装依赖失败
        pause
        exit /b 1
    )
    echo [OK] 依赖安装完成
) else (
    echo [OK] 依赖检查通过
)
echo.

REM 检查服务器文件
echo [3/3] 检查服务器文件...
if not exist pymol_mcp_server.py (
    echo [错误] 未找到 pymol_mcp_server.py
    pause
    exit /b 1
)
echo [OK] 服务器文件存在
echo.

echo ==========================================
echo    启动 HTTP 服务器
REM 启动服务器
echo [信息] 启动服务器，默认地址 http://127.0.0.1:3000
echo [信息] 在MCP客户端中配置URL: http://127.0.0.1:3000/sse
echo.
echo 按Ctrl+C停止服务器
echo ==========================================
echo.

python pymol_mcp_server.py --host 127.0.0.1 --port 3000

pause
