from typing import Optional

import asyncio
from pathlib import Path

import tomli as toml
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class _EventHandler(FileSystemEventHandler):
    def __init__(self, queue: asyncio.Queue, loop: asyncio.BaseEventLoop, *args, **kwargs):
        self._loop = loop
        self._queue = queue
        super(*args, **kwargs)

    def on_created(self, event: FileSystemEvent) -> None:
        self._loop.call_soon_threadsafe(self._queue.put_nowait, event)


class EventIterator(object):
    def __init__(self, queue: asyncio.Queue, loop: Optional[asyncio.BaseEventLoop] = None):
        self.queue = queue

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self.queue.get()

        if item is None:
            raise StopAsyncIteration

        return item


def watch(
    path: Path, queue: asyncio.Queue, loop: asyncio.BaseEventLoop, recursive: bool = False
) -> None:
    """Watch a directory for changes."""
    handler = _EventHandler(queue, loop)

    observer = Observer()
    observer.schedule(handler, str(path), recursive=recursive)
    observer.start()
    print("Observer started")
    observer.join(10)
    loop.call_soon_threadsafe(queue.put_nowait, None)


async def main(queue: asyncio.Queue, config: dict[str, str]) -> None:
    url = config["url"]
    token = config["token"]
    org = config["org"]
    bucket = config["bucket"]

    async for event in EventIterator(queue):
        print("Got an event!", event)
        async with InfluxDBClientAsync(url=url, token=token, org=org, enable_gzip=True) as client:

            # Stream of FluxRecords
            write_api = client.write_api()

            successfully = await write_api.write(bucket=bucket, record=[_point1, _point2])
            print(f" > successfully: {successfully}")


if __name__ == "__main__":
    """Sample code to run the server.

    Sample config.toml file:
    ```
        [influxdb]
        url = "http://localhost:8086"
        token = "my-token"
        org = "my-org"
        bucket = "my-bucket"

        [datasets]
        iris = "iris.csv"
    ```

    Raises:
        ValueError: If config.toml is not found.
    """
    toml_path = Path("config.toml")
    if toml_path.exists():
        with open(toml_path) as f:
            cfg = toml.load(f)
    else:
        raise ValueError("No configuration file found")

    loop = asyncio.new_event_loop()
    queue = asyncio.Queue(loop=loop)

    futures = [loop.run_in_executor(None, watch, Path("."), queue, loop, False), main(queue, cfg)]

    loop.run_until_complete()
