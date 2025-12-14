from __future__ import annotations

import os

# Backend API base URL for the local TestProduct API
# e.g. http://localhost:8000
BASE_URL = os.getenv("TESTPRODUCT_API_BASE_URL", "http://127.0.0.1:3001")

# Web app entry (authenticated area) for the Angular TestProduct UI
# e.g. http://localhost:4200/dashboard
UI_BASE_URL = os.getenv("TESTPRODUCT_UI_BASE_URL", "http://127.0.0.1:4201")
APP_URL = os.getenv("TESTPRODUCT_APP_URL", f"{UI_BASE_URL.rstrip('/')}/dashboard")

# API endpoint path for login (combined with BASE_URL)
# TestProduct exposes POST /login which returns a JWT token
LOGIN_API_PATH = os.getenv("TESTPRODUCT_LOGIN_API_PATH", "/login")

# Authentication storage configuration for TestProduct.
# We keep the existing constant names for compatibility with helpers:
# - AUTH_COOKIE_NAME: key used to store the JWT (in localStorage).
# - COOKIE_DOMAIN: origin for which storage is written (UI origin).
AUTH_COOKIE_NAME = os.getenv("TESTPRODUCT_AUTH_KEY", "token")
COOKIE_DOMAIN = os.getenv("TESTPRODUCT_AUTH_ORIGIN", UI_BASE_URL.rstrip("/"))

# Default API credentials for TestProduct (can be overridden via env vars):
#   TESTPRODUCT_USERNAME
#   TESTPRODUCT_PASSWORD
API_USERNAME = os.getenv("TESTPRODUCT_USERNAME", "user1")
API_PASSWORD = os.getenv("TESTPRODUCT_PASSWORD", "123456")
