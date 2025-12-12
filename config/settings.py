from __future__ import annotations

import os

# Base domain for the demo application and its API
BASE_URL = os.getenv("DEMO_BASE_URL", "https://practice.expandtesting.com")

# Web app entry (authenticated area)
APP_URL = os.getenv("DEMO_APP_URL", f"{BASE_URL}/notes/app")

# API endpoint path for login (combined with BASE_URL)
LOGIN_API_PATH = os.getenv("DEMO_LOGIN_API_PATH", "/notes/api/auth/login")

# Authentication cookie configuration for the demo app
AUTH_COOKIE_NAME = os.getenv("DEMO_AUTH_COOKIE_NAME", "token")
COOKIE_DOMAIN = os.getenv("DEMO_COOKIE_DOMAIN", "practice.expandtesting.com")

# Optional credentials or token can be provided via env vars:
#   DEMO_EMAIL       - Account email for the demo app
#   DEMO_PASSWORD    - Account password for the demo app
#   DEMO_JWT         - Optional pre-generated token to be set as the cookie value
