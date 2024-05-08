#!/usr/bin/env python3
import asyncio
import sys


async def l2rsplice(reader, writer):
    try:
        while True:
            data = await reader.read(8192)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except asyncio.TimeoutError:
        print("[!] Timeout error in l2r coroutine")
    except ConnectionResetError:
        print("[!] Connection reset error in l2r coroutine")
    finally:
        writer.close()
        await writer.wait_closed()

async def r2lsplice(reader, writer):
    try:
        while True:
            data = await reader.read(8192)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except asyncio.TimeoutError:
        print("[!] Timeout error in r2l coroutine")
    except ConnectionResetError:
        print("[!] Connection reset error in r2l coroutine")
    finally:
        writer.close()
        await writer.wait_closed()


async def handle_client(local_reader, local_writer, remote_host, remote_port):
    try:
        remote_reader, remote_writer = await asyncio.open_connection(remote_host, remote_port)
        client_socket_info = local_writer.get_extra_info('peername')
        print(f'[INFO] Client connected. {client_socket_info}')

        tasks = [
        asyncio.create_task(l2rsplice(local_reader, remote_writer)),
        asyncio.create_task(r2lsplice(remote_reader, local_writer))
    ]
        await asyncio.gather(*tasks)

    except ConnectionError as e:
        print(f'[!] Error {e}')
    except Exception as e:
        print(f'[!] {e}')
    finally:
        print('[*] Closing socket connection.')
        local_writer.close()
        await local_writer.wait_closed()



async def run_server(local_host, local_port, remote_host, remote_port):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, remote_host, remote_port), local_host, local_port)
    addr = server.sockets[0].getsockname()
    print(f'[INFO] {server}')
    print(f'[*] Listening for connections on {addr}')
    try:
        async with server:
            await server.serve_forever()
    finally:
        print(f'[*] Shutting down... listening: {server.is_serving()}')
        await asyncio.sleep(2)


async def main():
    if len(sys.argv[1:]) != 4:
        print("Usage: ./asyncproxy.py [local_host] [local_port]", end=' ')
        print("[remote_host] [remote_port]")
        print("Example: ./asyncproxy.py 127.0.0.1 9999 10.12.132.1 8888")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    server_task = asyncio.create_task(run_server(local_host, local_port, remote_host, remote_port))
    try:
        await server_task
    except RuntimeError as e:
        print(f'[!] Server did not exit cleanly!')
    except Exception as e:
        print(f'[!] {e}')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print(f'[!] KeyboardInterrupt')
