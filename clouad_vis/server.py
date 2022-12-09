from typing import Optional

import asyncio
import time
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

    def on_modified(self, event: FileSystemEvent) -> None:
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


<<<<<<< HEAD
def watch(path: Path, recursive: bool = False) -> None:
    """Watch a directory for changes then add to observer

    # Reference
    * https://gist.github.com/mivade/f4cb26c282d421a62e8b9a341c7c65f6
    """
    queue = asyncio.Queue()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
=======
def watch(datasets: dict[str, str]) -> None:
    """Watch a directory for changes then add to observer"""
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
>>>>>>> 3e469fb (Remote `loop` in arguments due to deprecation)
    handler = _EventHandler(queue, loop)

    observers = []
    observer = Observer()
<<<<<<< HEAD
    # Add path to observer
    observer.schedule(handler, path, recursive=recursive)

=======
    for dataset, path in datasets.items():
        print(f"Watching {dataset} at {path}")
        if path.exists():
            # Add path to observer
            observer.schedule(handler, path=Path(path).parent, recursive=False)

            # Add observable to list of observers
            observers.append(observer)
>>>>>>> 3e469fb (Remote `loop` in arguments due to deprecation)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    loop.call_soon_threadsafe(queue.put_nowait, None)


async def main(queue: asyncio.Queue, config: dict[str, str]) -> None:
    url = config["influxdb"]["url"]
    token = config["influxdb"]["token"]
    org = config["influxdb"]["org"]
    bucket = config["influxdb"]["bucket"]

    # Get current event loop
    loop = asyncio.get_event_loop()

    async for event in EventIterator(queue):
        print("Got an event!", event, event.src_path)
<<<<<<< HEAD
        if event.src_path in config["datasets"].values():
            print(f"Found a dataset! {event.src_path}")
=======
>>>>>>> 3e469fb (Remote `loop` in arguments due to deprecation)

        # async with InfluxDBClientAsync(url=url, token=token, org=org, enable_gzip=True) as client:

        #     # Stream of FluxRecords
        #     write_api = client.write_api()

        #     successfully = await write_api.write(bucket=bucket, record=[_point1, _point2])
        #     print(f" > successfully: {successfully}")


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
        with open(toml_path, "rb") as f:
            cfg = toml.load(f)
    else:
        raise ValueError("No configuration file found")

    loop = asyncio.new_event_loop()
    queue = asyncio.Queue()

    futures = [
<<<<<<< HEAD
        loop.run_in_executor(None, watch, Path("./sample"), True),
=======
        loop.run_in_executor(None, watch, cfg["datasets"]),
>>>>>>> 3e469fb (Remote `loop` in arguments due to deprecation)
        main(queue, cfg),
    ]

    loop.run_until_complete(asyncio.gather(*futures))
