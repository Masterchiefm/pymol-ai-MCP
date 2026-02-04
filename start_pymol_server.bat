@echo off
chcp 65001 >nul
echo ==========================================
echo    PyMOL AI Controller MCP Server
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python Not found，make sure Python is installed and added to PATH
    pause
    exit /b 1
)

REM Check PyMOL MCP server
if not exist "pymol_mcp_server.py" (
    echo Erro:  pymol_mcp_server.py not found
    echo make sure you run this script in mcp path.
    pause
    exit /b 1
)

echo Starting PyMOL MCP Server...
echo.
echo Make sure PyMOL in open and enabled XML-RPC server
echo   if pymol is opened, run "import pymol.rpc" and "pymol.rpc.launch_XMLRPC()" in pymol cmd
echo   Or you can run pymol in terminal in this way: pymol -R
echo.

python pymol_mcp_server.py

if errorlevel 1 (
    echo.
    echo Failed.
    pause
)
