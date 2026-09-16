import pytest

from src import config
from src.state import bootstrap


@pytest.fixture(scope="session")
def state():
    return bootstrap(config.DATA_DIR)
