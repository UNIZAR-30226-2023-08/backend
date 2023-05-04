from typing import List
from fastapi import WebSocket
from pydantic import BaseModel

class PlayerMessage(BaseModel):
    username: str
    message: str

class ChatManager:
    def __init__(self):
        self.active_chats = {}

    async def connect(self, websocket: WebSocket, chat_id: int, username: str):
        await websocket.accept()
        await self.join_chat(websocket, chat_id, username)
        await self.broadcast_message(chat_id, f"{username} has joined the chat.")

    async def receive(self, websocket: WebSocket, chat_id: int, username: str, message: str):
        player_message = PlayerMessage(username=username, message=message)
        await self.broadcast_message(chat_id, player_message.json())

    async def disconnect(self, websocket: WebSocket, chat_id: int, username: str):
        await self.remove_player(websocket, chat_id, username)
        await self.broadcast_message(chat_id, f"{username} has left the chat.")

    async def join_chat(self, websocket: WebSocket, chat_id: int, username: str):
        if chat_id not in self.active_chats:
            self.active_chats[chat_id] = []
        self.active_chats[chat_id].append((username, websocket))

    async def remove_player(self, websocket: WebSocket, chat_id: int, username: str):
        if chat_id in self.active_chats:
            self.active_chats[chat_id] = [(u, ws) for u, ws in self.active_chats[chat_id] if ws != websocket]

    async def broadcast_message(self, chat_id: int, message: str):
        if chat_id in self.active_chats:
            for _, ws in self.active_chats[chat_id]:
                await ws.send_text(message)
