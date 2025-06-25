import asyncio
import websockets
import json
import datetime
import os

CONNECTED_CLIENTS = set()

async def audio_server(websocket):
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    print(f"[{timestamp()}] Client connected: {client_id}")
    CONNECTED_CLIENTS.add(websocket)

    try:
        async for message in websocket:
            print(f"[{timestamp()}] Message received from {client_id}")
            try:
                data = json.loads(message)
                audio_data_b64 = data.get("audio_data")
                sender_id = data.get("sender_id")
                if audio_data_b64 and sender_id:
                    print(f"[{timestamp()}] Audio received from {sender_id} ({len(audio_data_b64)} bytes)")
                    for client in list(CONNECTED_CLIENTS):
                        if client != websocket:
                            try:
                                await client.send(message)
                                print(f"[{timestamp()}] Forwarded audio to client {client.remote_address}")
                            except websockets.exceptions.ConnectionClosed:
                                CONNECTED_CLIENTS.remove(client)
                                print(f"[{timestamp()}] Client {client.remote_address} disconnected during send.")
                else:
                    print(f"[{timestamp()}] Invalid message structure: {data}")
            except json.JSONDecodeError as e:
                print(f"[{timestamp()}] JSON decode error: {e}")
    except websockets.exceptions.ConnectionClosed:
        print(f"[{timestamp()}] Client disconnected: {client_id}")
    finally:
        CONNECTED_CLIENTS.remove(websocket)
        print(f"[{timestamp()}] Client removed. Active clients: {len(CONNECTED_CLIENTS)}")

def timestamp():
    return datetime.datetime.now().strftime('%H:%M:%S')

async def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"[{timestamp()}] Server starting on ws://0.0.0.0:{port}")
    async with websockets.serve(audio_server, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"[{timestamp()}] Server stopped by user.")
