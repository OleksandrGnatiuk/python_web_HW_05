import asyncio
import logging

import aiohttp
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from main import get_exchange

logging.basicConfig(level=logging.INFO)


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    print(f"Error status: {resp.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            m = message.strip().split()
            if len(m) == 1 and m[0] == 'exchange':
                exc = await get_exchange(1, [])
                await self.send_to_clients(exc)
            elif len(m) == 2 and m[0] == 'exchange':
                days = int(m[1])
                exc = await get_exchange(days, [])
                await self.send_to_clients(exc)
            elif len(m) > 2:
                days = int(message.split()[1])
                currs = message.split()[2:]
                exc = await get_exchange(days, currs)
                await self.send_to_clients(exc)
            elif message == 'Hi Server':
                await self.send_to_clients(f"{ws.name}: {message}")
                await self.send_to_clients('Привіт мої любі!')
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
