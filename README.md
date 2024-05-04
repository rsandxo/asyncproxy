# asyncproxy
Asynchronous TCP Proxy Server (Python 3.10+)

This is a simple TCP proxy server I wrote for fun as an exercise to learn how to use asyncio. It's fast, probably not too reliable, but it seems stable and works well for my use case. It is very bare-bones. The server listens on a provided address, and accepts packets from clients, forwards them to a remote host, receives packets from the remote host, and sends them back to the client. My testing showed that it handles multiple connections just fine.

## Instructions

```
Usage: ./asyncproxy.py [local_host] [local_port] [remote_host] [remote_port]
```

### Forward proxy example
```
Example: ./asyncproxy.py 127.0.0.1 9999 10.12.132.1 8888
```

### Reverse proxy example
```
Example: ./asyncproxy.py 0.0.0.0 9999 127.0.0.1 8888
```
