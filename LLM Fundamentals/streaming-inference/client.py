# client.py
import asyncio
import websockets

async def main():
    uri = "ws://localhost:8000/llm-stream"
    async with websockets.connect(uri) as ws:
        await ws.send("Write a poem about software development.")

        while True:
            token = await ws.recv()
            if token == "[END]":
                break
            print(token, end="", flush=True)

asyncio.run(main())
