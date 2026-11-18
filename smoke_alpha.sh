#!/usr/bin/env bash
# Smoke tests against the deployed v1 alpha; adds no rows to the query log. See tests/test_live_alpha.py.
EDOPS_ALPHA_URL=${EDOPS_ALPHA_URL:-https://edopsv1a.computingplace.org} python -m pytest tests/test_live_alpha.py -v
