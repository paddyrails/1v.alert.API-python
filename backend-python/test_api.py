import json
import time
import uuid

import requests

BASE_URL = "http://localhost:8002"

def pretty(resp):
    print(f"\n=== {resp.request.method} {resp.request.url} -> {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)


def main():
    # Unique email each run to avoid duplicate errors
    unique = str(uuid.uuid4())[:8]
    email = f"test_{unique}@example.com"
    password = "password123"
    name = "Test User"

    # 1. Health
    print("1) HEALTH")
    r = requests.get(f"{BASE_URL}/health")
    pretty(r)

    # 2. Register
    print("\n2) REGISTER")
    r = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    pretty(r)
    if r.status_code != 200:
        print("Register failed, aborting.")
        return

    data = r.json()
    access_token = data["accessToken"]
    refresh_token = data["refreshToken"]

    # 3. Login (just to confirm it works)
    print("\n3) LOGIN")
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password},
    )
    pretty(r)
    if r.status_code == 200:
        access_token = r.json()["accessToken"]
        refresh_token = r.json()["refreshToken"]

    auth_header = {"Authorization": f"Bearer {access_token}"}

    # 4. Create alertdef (protected)
    print("\n4) CREATE ALERTDEF")
    r = requests.post(
        f"{BASE_URL}/api/alertdefs",
        headers=auth_header,
        json={"name": "My First Alert", "description": "Created by test script"},
    )
    pretty(r)
    if r.status_code != 200:
        print("Create alertdef failed, aborting.")
        return

    alert_id = r.json()["id"]

    # 5. List alertdefs
    print("\n5) LIST ALERTDEFS")
    r = requests.get(
        f"{BASE_URL}/api/alertdefs",
        headers=auth_header,
        params={"page": 1, "limit": 10},
    )
    pretty(r)

    # 6. Get single alertdef
    print("\n6) GET ALERTDEF")
    r = requests.get(
        f"{BASE_URL}/api/alertdefs/{alert_id}",
        headers=auth_header,
    )
    pretty(r)

    # 7. Update alertdef
    print("\n7) UPDATE ALERTDEF")
    r = requests.patch(
        f"{BASE_URL}/api/alertdefs/{alert_id}",
        headers=auth_header,
        json={"name": "Updated Alert Name"},
    )
    pretty(r)

    # 8. Refresh token
    print("\n8) REFRESH TOKEN")
    r = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        json={"refreshToken": refresh_token},
    )
    pretty(r)
    if r.status_code == 200:
        new_access = r.json()["accessToken"]
        new_refresh = r.json()["refreshToken"]
        print(f"\nOld refresh token: {refresh_token}")
        print(f"New refresh token: {new_refresh}")
        access_token = new_access
        refresh_token = new_refresh
        auth_header = {"Authorization": f"Bearer {access_token}"}

    # 9. Logout (revoke current refresh token)
    print("\n9) LOGOUT")
    r = requests.post(
        f"{BASE_URL}/api/auth/logout",
        headers=auth_header,
        json={"refreshToken": refresh_token},
    )
    pretty(r)

    # 10. Try to refresh with revoked token (should fail 401)
    print("\n10) REFRESH WITH REVOKED TOKEN (EXPECT 401)")
    r = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        json={"refreshToken": refresh_token},
    )
    pretty(r)


if __name__ == "__main__":
    main()