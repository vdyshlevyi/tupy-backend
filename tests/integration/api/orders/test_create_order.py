import pytest
from httpx import AsyncClient
from starlette import status

from app.uow.unit_of_work import UnitOfWork
from tests.constants import Urls
from tests.factories import OrderFactory


@pytest.mark.anyio
async def test_create_order_invalid_coordinates(test_client: AsyncClient) -> None:
    """Test order creation with invalid coordinates."""
    response = await test_client.post(
        url=Urls.Orders.CREATE,
        json={
            "name": "Test Order",
            "description": "A test order",
            "start_point": {"lat": 100, "lng": 200},  # Invalid latitude and longitude
            "end_point": {"lat": 40.7128, "lng": -74.006},
            "distance_km": 5.2,
            "duration_minutes": 15.5,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_order_missing_required_fields(test_client: AsyncClient) -> None:
    """Test order creation with missing required fields."""
    response = await test_client.post(
        url=Urls.Orders.CREATE,
        json={
            "name": "Test Order",
            "description": "A test order",
            # Missing start_point and end_point
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_order_invalid_geometry_format(test_client: AsyncClient) -> None:
    """Test order creation with invalid geometry format."""
    response = await test_client.post(
        url=Urls.Orders.CREATE,
        json={
            "name": "Test Order",
            "description": "A test order",
            "start_point": "invalid geometry",  # Should be lat/lng object
            "end_point": {"lat": 40.7128, "lng": -74.006},
            "distance_km": 5.2,
            "duration_minutes": 15.5,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_order_success(
    test_client: AsyncClient,
    test_uow: UnitOfWork,
) -> None:
    """Test successful order creation."""
    order_data = {
        "name": "Central Park Order",
        "description": "A scenic order through Central Park",
        "start_point": {"lat": 40.7831, "lng": -73.9712},  # Central Park West
        "end_point": {"lat": 40.7829, "lng": -73.9581},  # Central Park East
        "distance_km": 2.5,
        "duration_minutes": 8.0,
    }

    response = await test_client.post(url=Urls.Orders.CREATE, json=order_data)
    assert response.status_code == status.HTTP_201_CREATED

    response_json = response.json()
    assert response_json.get("name") == order_data["name"]
    assert response_json.get("description") == order_data["description"]
    assert "id" in response_json

    # Verify that the order was created in the database
    db_order = await test_uow.order.get_by_id(id_=response_json["id"])
    assert db_order is not None, "Order should be created in the database"
    assert db_order.name == order_data["name"]
    assert db_order.description == order_data["description"]
    assert db_order.distance_km == order_data["distance_km"]
    assert db_order.duration_minutes == order_data["duration_minutes"]

    # Check that geometry points were saved correctly
    assert db_order.start_point is not None
    assert db_order.end_point is not None


@pytest.mark.anyio
async def test_create_order_minimal_data(
    test_client: AsyncClient,
    test_uow: UnitOfWork,
) -> None:
    """Test order creation with minimal required data."""
    order_data = {
        "name": "Minimal Order",
        "start_point": {"lat": 40.7831, "lng": -73.9712},
        "end_point": {"lat": 40.7829, "lng": -73.9581},
    }

    response = await test_client.post(url=Urls.Orders.CREATE, json=order_data)
    assert response.status_code == status.HTTP_201_CREATED

    response_json = response.json()
    assert response_json.get("name") == order_data["name"]
    assert "id" in response_json

    # Verify in database
    db_order = await test_uow.order.get_by_id(id_=response_json["id"])
    assert db_order is not None
    assert db_order.name == order_data["name"]
    assert db_order.description is None  # Should be nullable
    assert db_order.distance_km is None  # Should be nullable
    assert db_order.duration_minutes is None  # Should be nullable


@pytest.mark.anyio
async def test_create_order_duplicate_name_allowed(
    test_client: AsyncClient,
    test_uow: UnitOfWork,
) -> None:
    """Test that duplicate order names are allowed (unlike users with emails)."""
    # Create first order using factory
    order1 = await OrderFactory.create_(uow=test_uow, name="Duplicate Order")

    # Try to create another order with the same name
    order_data = {
        "name": "Duplicate Order",
        "description": "Another order with the same name",
        "start_point": {"lat": 40.7128, "lng": -74.006},
        "end_point": {"lat": 40.7306, "lng": -73.9352},
        "distance_km": 3.2,
        "duration_minutes": 12.0,
    }

    response = await test_client.post(url=Urls.Orders.CREATE, json=order_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Should succeed - duplicate names are allowed for orders
    response_json = response.json()
    assert response_json.get("name") == order_data["name"]
    assert response_json["id"] != order1.id  # Different IDs


@pytest.mark.anyio
@pytest.mark.parametrize(
    "order_data",
    [
        {
            "name": "Order in Europe",
            "start_point": {"lng": 2.3522, "lat": 48.8566},  # Paris
            "end_point": {"lng": 13.4050, "lat": 52.5200},  # Berlin
        },
        {
            "name": "Order in Asia",
            "start_point": {"lng": 139.6917, "lat": 35.6895},  # Tokyo
            "end_point": {"lng": 116.4074, "lat": 39.9042},  # Beijing
        },
        {
            "name": "Order crossing dateline",
            "start_point": {"lng": 179.0, "lat": 45.0},
            "end_point": {"lng": -179.0, "lat": 45.0},
        },
    ],
)
async def test_create_order_various_coordinate_ranges(
    test_client: AsyncClient,
    test_uow: UnitOfWork,
    order_data,
) -> None:
    """Test order creation with various valid coordinate ranges."""
    response = await test_client.post(url=Urls.Orders.CREATE, json=order_data)
    assert response.status_code == status.HTTP_201_CREATED, (
        f"Failed for case: {order_data['name']} -> {response.text}"
    )

    response_json = response.json()
    assert response_json.get("name") == order_data["name"]
