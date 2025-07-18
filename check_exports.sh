#!/bin/bash

# Script to check export files in the Odoo container

echo "Checking export files in Odoo container..."
echo "==========================================="

# Get the container name
CONTAINER_NAME=$(docker compose ps -q odoo17)

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ Odoo container not found. Make sure it's running with 'docker compose up -d'"
    exit 1
fi

echo "📦 Container: $CONTAINER_NAME"
echo ""

# Check if export directory exists
echo "🔍 Checking export directory..."
docker exec $CONTAINER_NAME ls -la /tmp/attendance_exports/ 2>/dev/null || {
    echo "📁 Export directory doesn't exist yet. It will be created when you run your first export."
    echo ""
    echo "🚀 To create test exports:"
    echo "   1. Access Odoo at http://localhost:10017"
    echo "   2. Create a database and install the attendance modules"
    echo "   3. Go to Attendance → Attendance Export → Export Wizard"
    echo ""
    exit 0
}

# List export files
echo "📄 Export files:"
docker exec $CONTAINER_NAME find /tmp/attendance_exports/ -name "*.json" -exec ls -lah {} \; 2>/dev/null || {
    echo "   No export files found yet."
}

echo ""
echo "🔧 To view export file contents:"
echo "   docker exec $CONTAINER_NAME cat /tmp/attendance_exports/filename.json"
echo ""
echo "💾 To copy export files to host:"
echo "   docker cp $CONTAINER_NAME:/tmp/attendance_exports/ ./exports/"
