#!/bin/bash

# Nightingale VoiceAI Professional Interface Launcher
# This script starts the complete professional healthcare system

echo "=========================================="
echo "  Nightingale VoiceAI Professional Suite"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check if backend is running
if ! curl -s http://localhost:8888/api/v1/health > /dev/null; then
    echo "Starting backend API service..."
    cd "$PROJECT_ROOT/src"
    PYTHONPATH="$PROJECT_ROOT/src" conda run -p "$PROJECT_ROOT/.venv" python -m uvicorn main:app --host 0.0.0.0 --port 8888 &
    sleep 5
    echo "✓ Backend service started on port 8888"
else
    echo "✓ Backend service already running on port 8888"
fi

# Start Professional Patient Interface
echo "Starting Professional Patient Interface..."
cd "$PROJECT_ROOT/ui"
conda run -p "$PROJECT_ROOT/.venv" python -m streamlit run patient_interface.py --server.port 8501 > /dev/null 2>&1 &
sleep 3
echo "✓ Professional Patient Portal started on port 8501"

# Start Professional Admin Dashboard  
echo "Starting Professional Admin Dashboard..."
conda run -p "$PROJECT_ROOT/.venv" python -m streamlit run admin_dashboard.py --server.port 8502 > /dev/null 2>&1 &
sleep 3
echo "✓ Professional Admin Dashboard started on port 8502"

echo ""
echo "=========================================="
echo "  Professional System Status"
echo "=========================================="
echo "✓ Backend API Service:     http://localhost:8888"
echo "✓ Patient Portal:          http://localhost:8501" 
echo "✓ Admin Dashboard:         http://localhost:8502"
echo ""
echo "Professional Interface Features:"
echo "• HIPAA compliant design"
echo "• Clinical grade workflows"
echo "• Professional terminology"
echo "• Comprehensive audit trails"
echo "• Real-time system monitoring"
echo ""
echo "Access the interfaces in your web browser."
echo "Press Ctrl+C to stop all services."
echo "=========================================="

# Wait for user interrupt
wait