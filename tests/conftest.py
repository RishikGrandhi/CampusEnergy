import pytest

from src.data import generate_synthetic_data
from src.features import build_features, chronological_split


@pytest.fixture(scope="session")
def raw_data():
    return generate_synthetic_data()


@pytest.fixture(scope="session")
def featured(raw_data):
    return build_features(raw_data)


@pytest.fixture(scope="session")
def splits(featured):
    return chronological_split(featured)

