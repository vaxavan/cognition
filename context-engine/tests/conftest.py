import pytest


@pytest.fixture
def sample_text():
    return "Test line\n\n" * 20
