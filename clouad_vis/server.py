import asyncio
from pathlib import Path

import tomli as toml
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync


async def main(config: dict[str, str]):
    url = config["url"]
    token = config["token"]
    org = config["org"]
    bucket = config["bucket"]

    async with InfluxDBClientAsync(url=url, token=token, org=org, enable_gzip=True) as client:

        # Stream of FluxRecords
        write_api = client.write_api()

        successfully = await write_api.write(bucket=bucket, record=[_point1, _point2])
        print(f" > successfully: {successfully}")


if __name__ == "__main__":
    toml_path = Path("config.toml")
    cfg = None
    if toml_path.exists():
        with open(toml_path) as f:
            cfg = toml.load(f)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(config=cfg))
