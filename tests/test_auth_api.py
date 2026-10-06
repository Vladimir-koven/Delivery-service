from httpx import AsyncClient


async def test_register_success(client: AsyncClient) -> None:
    payload = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "strong_password",
    }

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data  # не палим хеш
    assert "password" not in data


async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "dup@example.com",
        "full_name": "First",
        "password": "strong_password",
    }
    # Первая регистрация — ок
    r1 = await client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    # Вторая — 409
    r2 = await client.post("/auth/register", json=payload)

    assert r2.status_code == 409
    detail = r2.json()
    assert detail["error"]["code"] == "email_already_exists"


async def test_register_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "full_name": "Test",
            "password": "strong_password",
        },
    )
    assert response.status_code == 422


async def test_register_short_password(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={
            "email": "ok@example.com",
            "full_name": "Test",
            "password": "short",
        },
    )
    assert response.status_code == 422


async def test_login_success(client: AsyncClient, test_user: dict) -> None:
    response = await client.post(
        "/auth/login",
        data={
            "grant_type": "password",
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


async def test_login_wrong_password(client: AsyncClient, test_user: dict) -> None:
    response = await client.post(
        "/auth/login",
        data={
            "grant_type": "password",
            "username": test_user["email"],
            "password": "wrong_password",
        },
    )

    assert response.status_code == 401
    detail = response.json()
    assert detail["error"]["code"] == "invalid_credentials"


async def test_login_unknown_email(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        data={
            "grant_type": "password",
            "username": "nobody@example.com",
            "password": "any_password",
        },
    )

    assert response.status_code == 401


async def test_me_success(auth_client: AsyncClient, test_user: dict) -> None:
    response = await auth_client.get("/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]
    assert data["id"] == test_user["id"]


async def test_me_without_token(client: AsyncClient) -> None:
    response = await client.get("/auth/me")

    assert response.status_code == 401


async def test_me_with_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )

    assert response.status_code == 401