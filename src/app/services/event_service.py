from aiohttp import ClientSession
from src.configs.logger import logger

class EventService:
    async def get_events(self):
        GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0/me/events"
        access_token = "eyJ0eXAiOiJKV1QiLCJub25jZSI6IkNfV0s5LTNjQVlMdVJpQUh0ZWNrVmJESDM0dzV1VjJoWjEwRENac3RHUE0iLCJhbGciOiJSUzI1NiIsIng1dCI6Inp4ZWcyV09OcFRrd041R21lWWN1VGR0QzZKMCIsImtpZCI6Inp4ZWcyV09OcFRrd041R21lWWN1VGR0QzZKMCJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC82MjZlMzZmMy04MjU3LTQ1YjctOTQ5NS02YTM3MGY4OTI1MWYvIiwiaWF0IjoxNzMyMjA2MzU2LCJuYmYiOjE3MzIyMDYzNTYsImV4cCI6MTczMjIxMTY0MCwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkFZUUFlLzhZQUFBQXdtVGY3Y09FOGVLNkFsbVk2QWpyNWNqZG8vOVFkQldEM042dmpMbXpPQ1VrMmQxbnhXY0sxVG8yZ2piaElJcmx3VGFIZXZacmJMcjFrSUV4ZkRBcVF3MnpTVzRiYVRVZnlpbFgrbExMWC9HeXFKaWpCNnhWVW5PbHZjY1h1T2hsVmlwNy9hYXdFdkZoVGk4REVidlJFQkhMMG0xdk9sREx3T1JDejFHSUw5bz0iLCJhbHRzZWNpZCI6IjE6bGl2ZS5jb206MDAwM0JGRkQyMEUxOTgwQSIsImFtciI6WyJwd2QiLCJtZmEiXSwiYXBwX2Rpc3BsYXluYW1lIjoiek9EQyIsImFwcGlkIjoiODJmNmU0NmQtY2E0Yy00ODFhLTliMDgtOGQyYWI2NzFkYTE1IiwiYXBwaWRhY3IiOiIxIiwiZW1haWwiOiJ2cGhvYTM0QG91dGxvb2suY29tIiwiZmFtaWx5X25hbWUiOiJWYW4gUGh1IiwiZ2l2ZW5fbmFtZSI6IkhvYSIsImlkcCI6ImxpdmUuY29tIiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiMTE2LjEwOS42OS4xMDYiLCJuYW1lIjoiSG9hIFZhbiBQaHUiLCJvaWQiOiJmYmU4MjZhZC0xOWE2LTRlZDItOGUzZC01NTIyZmU2ZWM3YzkiLCJwbGF0ZiI6IjMiLCJwdWlkIjoiMTAwMzIwMDQwNUYwQTQ3NyIsInJoIjoiMS5BY1lBOHpadVlsZUN0MFdVbFdvM0Q0a2xId01BQUFBQUFBQUF3QUFBQUFBQUFBREdBSFhHQUEuIiwic2NwIjoiZW1haWwgb3BlbmlkIHByb2ZpbGUiLCJzaWduaW5fc3RhdGUiOlsia21zaSJdLCJzdWIiOiJwUVZDTF80Qmo0NGN6dUNlWjRhSDlyN0JWOVRtNnlqeGhDbW50YTRYbnZ3IiwidGVuYW50X3JlZ2lvbl9zY29wZSI6IkFTIiwidGlkIjoiNjI2ZTM2ZjMtODI1Ny00NWI3LTk0OTUtNmEzNzBmODkyNTFmIiwidW5pcXVlX25hbWUiOiJsaXZlLmNvbSN2cGhvYTM0QG91dGxvb2suY29tIiwidXRpIjoiU0I1NGw0bXg3MFNJc1p6T0ljR0dBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiNjJlOTAzOTQtNjlmNS00MjM3LTkxOTAtMDEyMTc3MTQ1ZTEwIiwiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19pZHJlbCI6IjEgMiIsInhtc19zdCI6eyJzdWIiOiJhcmR6Tl9XNk8yM0JaaTBkMm1hTUZwSFFKUFNjelF5UmE0UWlVZEk2RlhZIn0sInhtc190Y2R0IjoxNzMyMjA1MjMyfQ.V5OhhmcLQuWTMmFOqd2NJ_FhADCdSc3P5Kr-7638tKnOH0lwOQreaL8r_B4kD_TjFLUV7QvVGBzKJdIvaMUS5qahPYmhEfQ2kiKgAf8zNm2Wq3H6B297ffErjIt4T0TgotMU3KsB4TT9H0bECxXuDZHGcnBuW1254lpD-ShkCoa41ORkfwwnwE_xW2gprsPRxSOMs0NeU1gyr1oWmvRW2DRqjMlL-DhjY5-04MHI0DC_ZvB_LEhdLegCHYyO7D4eyEZnGc81PsahpRJVtNVu867v9-G9wWmu_-jIkkkckmix2qms1mvl0vfJFRaUDiPv2WaZDzBDZKDB3gfWYhnhkg"
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