#!/bin/bash
# scripts/health_check.sh
# Check all services health

SERVICES=("backend" "ai" "simulation" "frontend")
FAILED=0

for svc in "${SERVICES[@]}"; do
    echo -n "Checking $svc... "
    if curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
        echo "✅"
    else
        echo "❌"
        FAILED=1
    fi
done

if [ $FAILED -eq 0 ]; then
    echo "✅ All services healthy."
    exit 0
else
    echo "❌ Some services are unhealthy."
    exit 1
fi