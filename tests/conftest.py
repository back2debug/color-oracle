import os
import pytest

# Set test environment variables before any app imports
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-real")
# Force a known key so tests don't depend on the developer's shell setup
os.environ["VALID_API_KEYS"] = "test-api-key"
os.environ.setdefault("ENVIRONMENT", "test")
