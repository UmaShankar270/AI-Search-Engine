"""Pytest fixtures for AI module tests."""

import pytest


@pytest.fixture
def sample_query():
    return "machine learning framework for Python"


@pytest.fixture
def sample_repositories():
    """Return a list of fake Repository objects for testing."""
    return []


@pytest.fixture
def mock_embeddings():
    """Return pre-computed mock embedding vectors."""
    return []
