#!/bin/bash
# Unified script to run pytest with coverage and JUnit XML reporting across all Python microservices
set -e
SERVICES=(backend/apps/core backend/apps/crm backend/apps/erp backend/apps/construction backend/apps/chat services/identity/app)
for SERVICE in "${SERVICES[@]}"; do
  echo "Running tests in $SERVICE..."
  cd "$SERVICE"
  pytest --nomigrations --reuse-db --cov=. --cov-report=xml --junitxml=../../reports/junit-report-$(basename $SERVICE).xml
  cd -
done
