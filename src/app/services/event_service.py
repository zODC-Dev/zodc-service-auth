from aiohttp import ClientSession
from src.configs.logger import logger

class EventService:
    async def get_events(self):
        GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0/me/events"
        access_token = ""

        async with ClientSession() as session:
            async with session.get(
                GRAPH_API_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            ) as response:
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response content: {await response.text()}")
                return await response.json()
    
event_service = EventService()