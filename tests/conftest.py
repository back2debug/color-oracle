import os
import pytest

# Set test environment variables before any app imports
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-real")
os.environ.setdefault("VALID_API_KEYS", "dev-key-local")
os.environ.setdefault("ENVIRONMENT", "test")
