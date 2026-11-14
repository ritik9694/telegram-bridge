import httpx

import config


class XenovraAPI:
    def __init__(self):
        self.base_url = config.XENOVRA_URL
        self.client = httpx.AsyncClient(timeout=None)
        self.token = None

    async def login(self):
        if not config.XENOVRA_PASSWORD:
            raise ValueError("XENOVRA_PASSWORD is not configured")

        response = await self.client.post(
            f"{self.base_url}/api/auth/login",
            json={
                "email": config.XENOVRA_EMAIL,
                "password": config.XENOVRA_PASSWORD,
            },
        )
        response.raise_for_status()

        self.token = response.json()["access_token"]

        self.client.headers.update({
            "Authorization": f"Bearer {self.token}"
        })

        return True

    async def upload_video(self, file_path, title):
        if not self.token:
            raise RuntimeError("Please login first")

        if not config.STORAGE_ID:
            raise ValueError("STORAGE_ID is not configured")

        path = str(file_path)

        with open(path, "rb") as video:
            response = await self.client.post(
                f"{self.base_url}/api/videos/upload/{config.STORAGE_ID}",
                data={"title": title},
                files={
                    "file": (
                        file_path.name,
                        video,
                        "application/octet-stream",
                    )
                },
            )

        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
