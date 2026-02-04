#!/bin/bash
echo "=========================================="
echo "   PyMOL AI Controller MCP Server"
echo "=========================================="
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python not found. Please make sure Python is installed and added to PATH"
        exit 1
    else
        PYTHON_CMD="python3"
    fi
else
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version

# Check PyMOL MCP server
if [ ! -f "pymol_mcp_server.py" ]; then
    echo "Error: pymol_mcp_server.py not found"
    echo "Make sure you run this script in the pymol-ai-controller directory"
    exit 1
fi

echo ""
echo "Starting PyMOL MCP Server..."
echo ""
echo "Make sure PyMOL is open and XML-RPC server is enabled:"
echo "  If PyMOL is open, run 'import pymol.rpc' and 'pymol.rpc.launch_XMLRPC()' in PyMOL command line"
echo "  Or start PyMOL from terminal: pymol -R"
echo ""

$PYTHON_CMD pymol_mcp_server.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Failed to start server"
fi
