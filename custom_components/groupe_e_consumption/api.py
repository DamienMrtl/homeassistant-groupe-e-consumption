import aiohttp
import asyncio
from typing import Optional
from .const import (
    TOKEN_URL,
    CLIENT_ID,
    CLIENT_SECRET,
    SCOPE,
    _LOGGER,
)


class GroupeEConsumptionAPI:
    def __init__(self, hass):
        self.hass = hass
        self.session = aiohttp.ClientSession()

    async def authenticate(self, username: str, password: str) -> str | None:
        """Authenticate with the API using OAuth 2.0 password credentials grant type."""
        payload = {
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": username,
            "password": password,
            "scope": SCOPE,
        }

        async with self.session.post(TOKEN_URL, data=payload) as response:
            if response.status == 200:
                token_info = await response.json()
                _LOGGER.info("Successfully authenticated with Groupe E API")
                return token_info["access_token"]
            else:
                _LOGGER.error(
                    "Failed to authenticate with Groupe E API: %s", response.status
                )
                return None

    async def get_premise_id(self, token: str) -> str | None:
        """Get PremiseID from the API."""
        url = "https://my.groupe-e.ch/api/private/PremiseSet?$filter=IsValidForHistory%20eq%20true"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                premise_id = data["d"]["results"][0]["premiseID"]
                return premise_id
            else:
                _LOGGER.error(
                    "Failed to get PremiseID from Groupe E API: %s", response.status
                )
                return None

    async def get_partner_id(self, token: str) -> str | None:
        """Get PartnerID from the API."""
        url = "https://login.my.groupe-e.ch/realms/my-groupe-e/protocol/openid-connect/userinfo"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                partner_id = data["business_partner"][0]
                return partner_id
            else:
                _LOGGER.error(
                    "Failed to get PartnerID from Groupe E API: %s", response.status
                )
                return None

    async def get_data(
        self,
        token: str,
        premise_id: str,
        partner_id: str,
        start_timestamp: int,
        end_timestamp: int,
        resolution: str,
    ) -> dict | None:
        """Get data from the API using the bearer token."""
        url = "https://my.groupe-e.ch/api/smartmeter-data"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {
            "premise": premise_id,
            "partner": partner_id,
            "start": start_timestamp,
            "end": end_timestamp,
            "resolution": resolution,
        }
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                _LOGGER.error(
                    "Failed to get data from Groupe E API: %s", response.status
                )
                return None

    async def close(self) -> None:
        """Close the aiohttp session."""
        await self.session.close()
