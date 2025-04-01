import json
from typing import Any, Dict

from nats.aio.client import Client
from nats.aio.msg import Msg

from src.configs.logger import log
from src.configs.settings import settings
from src.domain.services.nats_service import INATSService, MessageCallback, RequestReplyCallback


class NATSService(INATSService):
    def __init__(self) -> None:
        self._client: Client = Client()
        self._is_connected: bool = False

    async def connect(self) -> None:
        """Connect to NATS server"""
        try:
            if not self._is_connected:
                await self._client.connect(
                    servers=[settings.NATS_URL],
                    name=settings.NATS_CLIENT_NAME,
                    reconnect_time_wait=3,
                    max_reconnect_attempts=5,
                    connect_timeout=5,
                    user=settings.NATS_USERNAME,
                    password=settings.NATS_PASSWORD
                )
                self._is_connected = True
                log.info(f"Connected to NATS server at {settings.NATS_URL}")
        except Exception as e:
            log.error(f"Failed to connect to NATS: {str(e)}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from NATS server"""
        if self._is_connected:
            await self._client.drain()
            self._is_connected = False
            log.info("Disconnected from NATS server")

    async def publish(self, subject: str, message: Dict[str, Any]) -> None:
        """Publish message to a subject"""
        try:
            if not self._is_connected:
                await self.connect()

            payload = json.dumps(message).encode()
            await self._client.publish(subject, payload)
            log.debug(f"Published message to {subject}: {message}")
        except Exception as e:
            log.error(f"Failed to publish message: {str(e)}")
            raise

    async def subscribe(self, subject: str, callback: MessageCallback) -> None:
        """Subscribe to a subject"""
        try:
            if not self._is_connected:
                await self.connect()

            async def message_handler(msg: Msg) -> None:
                try:
                    data = json.loads(msg.data.decode())
                    await callback(msg.subject, data)
                except Exception as e:
                    log.error(f"Error processing message: {str(e)}")

            await self._client.subscribe(subject, cb=message_handler)
            log.info(f"Subscribed to {subject}")
        except Exception as e:
            log.error(f"Failed to subscribe: {str(e)}")
            raise

    async def request(self, subject: str, message: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """Send request and wait for response"""
        try:
            if not self._is_connected:
                await self.connect()

            payload = json.dumps(message).encode()
            response = await self._client.request(subject, payload, timeout=timeout)
            return json.loads(response.data.decode()) if response.data else {}
        except Exception as e:
            log.error(f"Failed to send request: {str(e)}")
            raise

    async def subscribe_request(self, subject: str, callback: RequestReplyCallback) -> None:
        """Subscribe to a subject for handling request-reply"""
        try:
            if not self._is_connected:
                await self.connect()

            async def message_handler(msg: Msg) -> None:
                try:
                    data = json.loads(msg.data.decode())

                    async def respond(response_data: Dict[str, Any]) -> None:
                        """Helper function to respond to the request"""
                        response_payload = json.dumps(response_data).encode()
                        await msg.respond(response_payload)

                    # Call the callback with subject, data and respond function
                    await callback(msg.subject, data, respond)
                except Exception as e:
                    log.error(f"Error processing request message: {str(e)}")
                    # Send error response if an exception occurs
                    error_response = {
                        "success": False,
                        "message": f"Error processing request: {str(e)}",
                        "error_code": "INTERNAL_ERROR"
                    }
                    await msg.respond(json.dumps(error_response).encode())

            await self._client.subscribe(subject, cb=message_handler)
            log.info(f"Subscribed to request subject: {subject}")
        except Exception as e:
            log.error(f"Failed to subscribe to request: {str(e)}")
            raise
