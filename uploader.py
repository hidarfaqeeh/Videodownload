import asyncio
import logging
from typing import Optional

from pyrogram import Client

logger = logging.getLogger(__name__)


class PyrogramUploader:
    def __init__(self, bot_token: str, api_id: int, api_hash: str, workers: int = 8):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.workers = workers
        self._client: Optional[Client] = None

    async def start(self) -> None:
        if self._client is None:
            self._client = Client(
                name="bot_uploader",
                api_id=self.api_id,
                api_hash=self.api_hash,
                bot_token=self.bot_token,
                workers=self.workers,
                in_memory=True,
                parse_mode=None,
            )
        if not self._client.is_connected:
            await self._client.start()
            logger.info("Pyrogram client started for uploads")

    async def stop(self) -> None:
        if self._client and self._client.is_connected:
            await self._client.stop()
            logger.info("Pyrogram client stopped")

    async def send_video(self, chat_id: int, file_path: str, caption: Optional[str] = None,
                         duration: Optional[int] = None, width: Optional[int] = None,
                         height: Optional[int] = None, parse_mode: Optional[str] = None) -> None:
        if not self._client:
            raise RuntimeError("Pyrogram client is not started")
        await self._client.send_video(
            chat_id=chat_id,
            video=file_path,
            caption=caption,
            duration=duration,
            width=width,
            height=height,
            supports_streaming=True,
            disable_notification=False,
        )

    async def send_document(self, chat_id: int, file_path: str, caption: Optional[str] = None) -> None:
        if not self._client:
            raise RuntimeError("Pyrogram client is not started")
        await self._client.send_document(
            chat_id=chat_id,
            document=file_path,
            caption=caption,
            disable_notification=False,
        )

