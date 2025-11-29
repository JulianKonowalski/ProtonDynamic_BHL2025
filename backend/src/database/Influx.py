import os
import json
from influxdb_client import WriteApi, QueryApi, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class Influxdb:

    bucket: str = "main"
    organization: str = "BHL"

    client: InfluxDBClient | None = None
    write_api: WriteApi | None = None
    query_api: QueryApi | None = None

    def __init__(self) -> None:
        self.client = InfluxDBClient(
            url="http://localhost:8086", 
            token=os.getenv("INFLUXDB_TOKEN"), 
            org=self.organization
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def writeRecord(self, sensor_id: int, temperature: float, humidity: float) -> None:
        self.write_api.write(
            bucket=self.bucket, 
            org=self.organization, 
            record=(Point("environ")
                .tag("sensor_id", sensor_id)
                .field("temperature", temperature)
                .field("humidity", humidity))
        )

    def readRecords(self, duration="10m"):
        query = f"""from(bucket: "{self.bucket}")
            |> range(start: -{duration})
            |> filter(fn: (r) => r._measurement == "environ")"""
        return [
            { 
                "sensor_id": record["sensor_id"],
                "field": record["_field"],
                "value": record["_value"],
                "time": record["_time"]
            } for record in json.loads(self.query_api.query(query, org="BHL").to_json())
        ]