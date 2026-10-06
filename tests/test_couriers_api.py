from httpx import AsyncClient

from delivery.schemas.courier import CourierStatus


async def test_create_courier(auth_client: AsyncClient) -> None:
    payload = {"full_name": "Ivan Petrov", "phone": "+79991234567"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Ivan Petrov"
    assert data["phone"] == "+79991234567"
    assert data["status"] == CourierStatus.OFFLINE
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_create_courier_validation_error(auth_client: AsyncClient) -> None:
    payload = {"full_name": "A", "phone": "+7"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 422


async def test_list_couriers_empty(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/couriers")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_couriers(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/couriers", json={"full_name": "Ivan", "phone": "+79991112233"}
    )
    await auth_client.post(
        "/couriers", json={"full_name": "Petr", "phone": "+79994445566"}
    )

    response = await auth_client.get("/couriers")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


async def test_list_couriers_filter_by_status(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/couriers",
        json={
            "full_name": "Ivan",
            "phone": "+79991112233",
            "status": "available",
        },
    )
    await auth_client.post(
        "/couriers",
        json={
            "full_name": "Petr",
            "phone": "+79994445566",
            "status": "offline",
        },
    )

    response = await auth_client.get("/couriers", params={"status": "available"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "available"


async def test_get_courier_by_id(auth_client: AsyncClient) -> None:
    created = await auth_client.post(
        "/couriers", json={"full_name": "Ivan", "phone": "+79991112233"}
    )
    courier_id = created.json()["id"]

    response = await auth_client.get(f"/couriers/{courier_id}")

    assert response.status_code == 200
    assert response.json()["id"] == courier_id


async def test_get_courier_not_found(auth_client: AsyncClient) -> None:
    missing_id = "00000000-0000-0000-0000-000000000000"

    response = await auth_client.get(f"/couriers/{missing_id}")

    assert response.status_code == 404


async def test_update_courier(auth_client: AsyncClient) -> None:
    created = await auth_client.post(
        "/couriers", json={"full_name": "Ivan", "phone": "+79991112233"}
    )
    courier_id = created.json()["id"]

    response = await auth_client.patch(
        f"/couriers/{courier_id}", json={"status": "available"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "available"
    # Остальные поля не изменились
    assert data["full_name"] == "Ivan"
    assert data["phone"] == "+79991112233"


async def test_update_courier_not_found(auth_client: AsyncClient) -> None:
    missing_id = "00000000-0000-0000-0000-000000000000"

    response = await auth_client.patch(
        f"/couriers/{missing_id}", json={"status": "available"}
    )

    assert response.status_code == 404


async def test_delete_courier(auth_client: AsyncClient) -> None:
    created = await auth_client.post(
        "/couriers", json={"full_name": "Ivan", "phone": "+79991112233"}
    )
    courier_id = created.json()["id"]

    response = await auth_client.delete(f"/couriers/{courier_id}")
    assert response.status_code == 204

    # Проверяем, что удалён
    check = await auth_client.get(f"/couriers/{courier_id}")
    assert check.status_code == 404


async def test_delete_courier_not_found(auth_client: AsyncClient) -> None:
    missing_id = "00000000-0000-0000-0000-000000000000"

    response = await auth_client.delete(f"/couriers/{missing_id}")

    assert response.status_code == 404


async def test_create_courier_min_length_full_name(auth_client: AsyncClient) -> None:
    """Ровно 2 символа — минимально допустимая длина."""
    payload = {"full_name": "Ив", "phone": "+79991234567"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 201
    assert response.json()["full_name"] == "Ив"


async def test_create_courier_max_length_full_name(auth_client: AsyncClient) -> None:
    """Ровно 100 символов — максимальная длина."""
    payload = {"full_name": "A" * 100, "phone": "+79991234567"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 201


async def test_create_courier_full_name_too_long(auth_client: AsyncClient) -> None:
    """101 символ — превышение максимума."""
    payload = {"full_name": "A" * 101, "phone": "+79991234567"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 422


async def test_create_courier_full_name_too_short(auth_client: AsyncClient) -> None:
    """1 символ — меньше минимума."""
    payload = {"full_name": "A", "phone": "+79991234567"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 422


async def test_create_courier_phone_min_length(auth_client: AsyncClient) -> None:
    """Ровно 5 символов — минимальная длина."""
    payload = {"full_name": "Ivan", "phone": "12345"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 201


async def test_create_courier_phone_too_short(auth_client: AsyncClient) -> None:
    payload = {"full_name": "Ivan", "phone": "1234"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 422


async def test_create_courier_phone_too_long(auth_client: AsyncClient) -> None:
    payload = {"full_name": "Ivan", "phone": "1" * 21}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 422


async def test_create_courier_missing_phone(auth_client: AsyncClient) -> None:
    response = await auth_client.post("/couriers", json={"full_name": "Ivan"})

    assert response.status_code == 422


async def test_create_courier_missing_full_name(auth_client: AsyncClient) -> None:
    response = await auth_client.post("/couriers", json={"phone": "+79991234567"})

    assert response.status_code == 422


async def test_create_courier_empty_body(auth_client: AsyncClient) -> None:
    response = await auth_client.post("/couriers", json={})

    assert response.status_code == 422


async def test_create_courier_wrong_type_full_name(auth_client: AsyncClient) -> None:
    """Число вместо строки."""
    response = await auth_client.post(
        "/couriers", json={"full_name": 123, "phone": "+79991234567"}
    )

    assert response.status_code == 422


async def test_create_courier_invalid_status(auth_client: AsyncClient) -> None:
    payload = {
        "full_name": "Ivan",
        "phone": "+79991234567",
        "status": "unknown_status",
    }

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 422


async def test_list_couriers_invalid_status(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/couriers", params={"status": "invalid"})

    assert response.status_code == 422


async def test_get_courier_invalid_uuid(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/couriers/not-a-uuid")

    assert response.status_code == 422


async def test_update_courier_invalid_uuid(auth_client: AsyncClient) -> None:
    response = await auth_client.patch(
        "/couriers/not-a-uuid", json={"status": "available"}
    )

    assert response.status_code == 422


async def test_delete_courier_invalid_uuid(auth_client: AsyncClient) -> None:
    response = await auth_client.delete("/couriers/not-a-uuid")

    assert response.status_code == 422


async def test_update_courier_empty_body_no_changes(auth_client: AsyncClient) -> None:
    """PATCH с пустым телом — 200, ничего не меняется."""
    created = await auth_client.post(
        "/couriers", json={"full_name": "Ivan", "phone": "+79991234567"}
    )
    before = created.json()

    response = await auth_client.patch(f"/couriers/{before['id']}", json={})

    assert response.status_code == 200
    after = response.json()
    assert after["full_name"] == before["full_name"]
    assert after["phone"] == before["phone"]
    assert after["status"] == before["status"]


async def test_update_courier_multiple_fields(auth_client: AsyncClient) -> None:
    """PATCH обновляет несколько полей сразу."""
    created = await auth_client.post(
        "/couriers", json={"full_name": "Ivan", "phone": "+79991234567"}
    )
    courier_id = created.json()["id"]

    response = await auth_client.patch(
        f"/couriers/{courier_id}",
        json={
            "full_name": "Petr",
            "phone": "+79990001122",
            "status": "busy",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Petr"
    assert data["phone"] == "+79990001122"
    assert data["status"] == "busy"


async def test_update_courier_invalid_status(auth_client: AsyncClient) -> None:
    created = await auth_client.post(
        "/couriers", json={"full_name": "Ivan", "phone": "+79991234567"}
    )
    courier_id = created.json()["id"]

    response = await auth_client.patch(
        f"/couriers/{courier_id}", json={"status": "unknown"}
    )

    assert response.status_code == 422


# ---------- Edge cases: idempotency ----------
async def test_delete_courier_twice(auth_client: AsyncClient) -> None:
    """Первое удаление — 204, второе — 404."""
    created = await auth_client.post(
        "/couriers", json={"full_name": "Ivan", "phone": "+79991234567"}
    )
    courier_id = created.json()["id"]

    first = await auth_client.delete(f"/couriers/{courier_id}")
    assert first.status_code == 204

    second = await auth_client.delete(f"/couriers/{courier_id}")
    assert second.status_code == 404



async def test_create_courier_unicode_full_name(auth_client: AsyncClient) -> None:
    """Русские буквы и эмодзи в имени."""
    payload = {"full_name": "Иван 🚀 Петров", "phone": "+79991234567"}

    response = await auth_client.post("/couriers", json=payload)

    assert response.status_code == 201
    assert response.json()["full_name"] == "Иван 🚀 Петров"


async def test_list_couriers_ordering_desc(auth_client: AsyncClient) -> None:
    """Курьеры возвращаются в порядке created_at DESC."""
    first = await auth_client.post(
        "/couriers", json={"full_name": "First", "phone": "+79991111111"}
    )
    second = await auth_client.post(
        "/couriers", json={"full_name": "Second", "phone": "+79992222222"}
    )

    response = await auth_client.get("/couriers")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Оба курьера на месте (порядок не проверяем —
    # при одинаковом created_at он определяется случайным UUID)
    ids = {data[0]["id"], data[1]["id"]}
    assert ids == {first.json()["id"], second.json()["id"]}

    # Сортировка по created_at DESC — проверяем неубывание
    assert data[0]["created_at"] >= data[1]["created_at"]


