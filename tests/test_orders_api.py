from decimal import Decimal
from uuid import uuid4

from httpx import AsyncClient


async def _create_courier(
    client: AsyncClient,
    *,
    full_name: str = "Courier",
    phone: str = "+79991112233",
    status: str = "available",
) -> dict:
    """Хелпер: создать курьера, вернуть JSON."""
    response = await client.post(
        "/couriers",
        json={"full_name": full_name, "phone": phone, "status": status},
    )
    assert response.status_code == 201
    return response.json()


async def _create_order(
    client: AsyncClient,
    *,
    customer_name: str = "Alice",
    customer_phone: str = "+79995556677",
    address: str = "ул. Пушкина, д. 1",
    total_amount: str = "1500.50",
) -> dict:
    """Хелпер: создать заказ, вернуть JSON."""
    response = await client.post(
        "/orders",
        json={
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "address": address,
            "total_amount": total_amount,
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_create_order(client: AsyncClient) -> None:
    payload = {
        "customer_name": "Alice",
        "customer_phone": "+79995556677",
        "address": "ул. Пушкина, д. 1",
        "total_amount": "1500.50",
    }

    response = await client.post("/orders", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Alice"
    assert data["customer_phone"] == "+79995556677"
    assert data["address"] == "ул. Пушкина, д. 1"
    assert Decimal(data["total_amount"]) == Decimal("1500.50")
    assert data["status"] == "created"
    assert data["courier_id"] is None
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_create_order_invalid_amount(client: AsyncClient) -> None:
    payload = {
        "customer_name": "Alice",
        "customer_phone": "+79995556677",
        "address": "ул. Пушкина, д. 1",
        "total_amount": "0",
    }

    response = await client.post("/orders", json=payload)

    assert response.status_code == 422


async def test_create_order_empty_body(client: AsyncClient) -> None:
    response = await client.post("/orders", json={})

    assert response.status_code == 422


async def test_list_orders_empty(client: AsyncClient) -> None:
    response = await client.get("/orders")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_orders(client: AsyncClient) -> None:
    await _create_order(client, customer_name="Alice")
    await _create_order(client, customer_name="Bob")

    response = await client.get("/orders")

    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_list_orders_filter_by_status(client: AsyncClient) -> None:
    await _create_order(client, customer_name="Alice")
    await _create_order(client, customer_name="Bob")

    response = await client.get("/orders", params={"status": "created"})

    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/orders", params={"status": "assigned"})

    assert response.status_code == 200
    assert response.json() == []


async def test_list_orders_invalid_status(client: AsyncClient) -> None:
    response = await client.get("/orders", params={"status": "unknown"})

    assert response.status_code == 422


async def test_get_order_by_id(client: AsyncClient) -> None:
    created = await _create_order(client)

    response = await client.get(f"/orders/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_order_not_found(client: AsyncClient) -> None:
    response = await client.get(f"/orders/{uuid4()}")

    assert response.status_code == 404


async def test_update_order(client: AsyncClient) -> None:
    created = await _create_order(client)

    response = await client.patch(
        f"/orders/{created['id']}",
        json={"customer_name": "Bob", "address": "Новый адрес"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Bob"
    assert data["address"] == "Новый адрес"
    # Не тронутые поля
    assert data["customer_phone"] == created["customer_phone"]


async def test_update_order_not_found(client: AsyncClient) -> None:
    response = await client.patch(
        f"/orders/{uuid4()}", json={"customer_name": "Bob"}
    )

    assert response.status_code == 404


async def test_delete_order(client: AsyncClient) -> None:
    created = await _create_order(client)

    response = await client.delete(f"/orders/{created['id']}")
    assert response.status_code == 204

    check = await client.get(f"/orders/{created['id']}")
    assert check.status_code == 404


async def test_delete_order_not_found(client: AsyncClient) -> None:
    response = await client.delete(f"/orders/{uuid4()}")

    assert response.status_code == 404


async def test_assign_courier(client: AsyncClient) -> None:
    courier = await _create_courier(client)
    order = await _create_order(client)

    response = await client.post(
        f"/orders/{order['id']}/assign",
        json={"courier_id": courier["id"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["courier_id"] == courier["id"]
    assert data["status"] == "assigned"

    # Курьер стал busy
    check = await client.get(f"/couriers/{courier['id']}")
    assert check.json()["status"] == "busy"


async def test_assign_courier_order_not_found(client: AsyncClient) -> None:
    courier = await _create_courier(client)

    response = await client.post(
        f"/orders/{uuid4()}/assign", json={"courier_id": courier["id"]}
    )

    assert response.status_code == 404


async def test_assign_courier_courier_not_found(client: AsyncClient) -> None:
    order = await _create_order(client)

    response = await client.post(
        f"/orders/{order['id']}/assign", json={"courier_id": str(uuid4())}
    )

    assert response.status_code == 404


async def test_assign_courier_busy_courier(client: AsyncClient) -> None:
    courier = await _create_courier(client)
    order1 = await _create_order(client)
    order2 = await _create_order(client)

    # Назначаем курьера на первый заказ — он становится busy
    await client.post(
        f"/orders/{order1['id']}/assign", json={"courier_id": courier["id"]}
    )

    # Пытаемся назначить на второй заказ — 409
    response = await client.post(
        f"/orders/{order2['id']}/assign", json={"courier_id": courier["id"]}
    )

    assert response.status_code == 409


async def test_assign_courier_to_assigned_order(client: AsyncClient) -> None:
    courier1 = await _create_courier(client, phone="+79991112233")
    courier2 = await _create_courier(client, phone="+79994445566")
    order = await _create_order(client)

    # Первый assign — ок
    await client.post(
        f"/orders/{order['id']}/assign", json={"courier_id": courier1["id"]}
    )

    # Второй assign — 409
    response = await client.post(
        f"/orders/{order['id']}/assign", json={"courier_id": courier2["id"]}
    )

    assert response.status_code == 409


async def test_update_status_happy_path(client: AsyncClient) -> None:
    """Полный сценарий: created → assigned → in_progress → delivered."""
    courier = await _create_courier(client)
    order = await _create_order(client)

    # assign
    r = await client.post(
        f"/orders/{order['id']}/assign", json={"courier_id": courier["id"]}
    )
    assert r.status_code == 200

    # in_progress
    r = await client.patch(
        f"/orders/{order['id']}/status", json={"status": "in_progress"}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"

    # delivered
    r = await client.patch(
        f"/orders/{order['id']}/status", json={"status": "delivered"}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "delivered"

    # Курьер снова available
    c = await client.get(f"/couriers/{courier['id']}")
    assert c.json()["status"] == "available"


async def test_update_status_invalid_transition(client: AsyncClient) -> None:
    """created → delivered — недопустимо."""
    order = await _create_order(client)

    response = await client.patch(
        f"/orders/{order['id']}/status", json={"status": "delivered"}
    )

    assert response.status_code == 409


async def test_update_status_cancel_from_created(client: AsyncClient) -> None:
    order = await _create_order(client)

    response = await client.patch(
        f"/orders/{order['id']}/status", json={"status": "cancelled"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_update_status_cancel_releases_courier(client: AsyncClient) -> None:
    courier = await _create_courier(client)
    order = await _create_order(client)

    await client.post(
        f"/orders/{order['id']}/assign", json={"courier_id": courier["id"]}
    )
    response = await client.patch(
        f"/orders/{order['id']}/status", json={"status": "cancelled"}
    )
    assert response.status_code == 200

    c = await client.get(f"/couriers/{courier['id']}")
    assert c.json()["status"] == "available"


async def test_update_status_order_not_found(client: AsyncClient) -> None:
    response = await client.patch(
        f"/orders/{uuid4()}/status", json={"status": "cancelled"}
    )

    assert response.status_code == 404


async def test_update_status_invalid_value(client: AsyncClient) -> None:
    order = await _create_order(client)

    response = await client.patch(
        f"/orders/{order['id']}/status", json={"status": "unknown"}
    )

    assert response.status_code == 422