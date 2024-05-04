#!/usr/bin/env python3
import asyncio
import sys


async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            writer.write(await reader.read(16384))
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def handle_client(local_reader, local_writer, remote_host, remote_port):
    try:
        remote_reader, remote_writer = await asyncio.open_connection(remote_host, remote_port)
        print(f'[*] Client connected.')
        l2r = pipe(local_reader, remote_writer)
        r2l = pipe(remote_reader, local_writer)
        await asyncio.gather(l2r, r2l)
    except ConnectionResetError as e:
        print(f'[!] Error: {e}')
    except ConnectionRefusedError as e:
        print(f'[!] Error: {e}')
    finally:
        print('[*] Closing socket connection.')
        local_writer.close()
        await local_writer.wait_closed()


async def run_server(local_host, local_port, remote_host, remote_port):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, remote_host, remote_port), local_host, local_port)
    addr = server.sockets[0].getsockname()
    print(server)
    print(f'[*] Listening for connections on {addr}')
    try:
        async with server:
            await server.serve_forever()
    finally:
        print(f'[!] Shutting down... serving={server.is_serving()}')
        await asyncio.sleep(2)


async def main():
    if len(sys.argv[1:]) != 4:
        print("Usage: ./aproxy.py [local_host] [local_port]", end='')
        print("[remote_host] [remote_port]")
        print("Example: ./aproxy.py 127.0.0.1 9000 10.12.132.1 9000")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    server_task = asyncio.create_task(run_server(local_host, local_port, remote_host, remote_port))
    try:
        await server_task
    except asyncio.CancelledError:
        if not asyncio.current_task().cancelling():
            raise
        else:
            return
    else:
        raise RuntimeError("[!] Task did not exit cleanly! This isn't normal behaviour.")


if __name__ == '__main__':
    asyncio.run(main())
