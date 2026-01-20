#!/bin/bash
# PRODUCTION TEST SUITE - QUICK START GUIDE
# Run tests on port 11000 with actual responses

set -e

BASE_DIR="/Users/vishaljha/CLM_Backend"
cd "$BASE_DIR"

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║              PRODUCTION TEST SUITE - PORT 11000 QUICK START                    ║"
echo "║  Tests: Validation, Metadata, Classification, Summarization, Performance      ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check if Django server is running
echo "STEP 1: Checking Django Server Status..."
if lsof -i :11000 > /dev/null 2>&1; then
    echo "✓ Django server already running on port 11000"
else
    echo "⚠ Starting Django server on port 11000..."
    python3 manage.py runserver 0.0.0.0:11000 > /dev/null 2>&1 &
    echo "  Waiting for server startup (10 seconds)..."
    sleep 10
    echo "✓ Django server started"
fi

echo ""
echo "STEP 2: Running Production Test Suite..."
echo ""

# Step 2: Run the test
python3 test_production_final.py

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                              TEST COMPLETE                                     ║"
echo "║  For detailed results, see: PRODUCTION_TEST_RESULTS_PORT_11000.md              ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
