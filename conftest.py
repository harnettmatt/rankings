import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth.utils import verify_token
from database.database import get_session
from database.database_service import DatabaseService
from group import models as group_models
from group import schemas as group_schemas
from item import models as item_models
from item import schemas as item_schemas
from main import APP
from membership import models as membership_models
from membership import schemas as membership_schemas
from persistable.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_token():
    return True


APP.dependency_overrides[get_session] = override_get_session
APP.dependency_overrides[verify_token] = override_get_token


@pytest.fixture(name="test_client")
def fixture_test_client():
    return TestClient(APP)


@pytest.fixture(name="mock_group")
def mock_group() -> group_models.Group:
    group_input = group_schemas.GroupCreate(name="Ramen")
    return DatabaseService(next(override_get_session())).create(
        input_schema=group_input, model_type=group_models.Group
    )


@pytest.fixture(name="mock_item")
def mock_item() -> item_models.Item:
    item_input = item_schemas.ItemCreate(name="Minca")
    return DatabaseService(next(override_get_session())).create(
        input_schema=item_input, model_type=item_models.Item
    )


@pytest.fixture(name="mock_membership")
def mock_membership(mock_group, mock_item) -> membership_models.Membership:
    membership_input = membership_schemas.MembershipCreate(
        group_id=mock_group.id, item_id=mock_item.id
    )
    return DatabaseService(next(override_get_session())).create(
        input_schema=membership_input, model_type=membership_models.Membership
    )
