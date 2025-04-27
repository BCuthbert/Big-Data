import csv
import time
import random
import os
from datetime import datetime, timezone

filename = "data.csv"
headers = ["timestamp", "sensor_value"]
dataSize = 20
updateTime = 10

if os.path.exists(filename):
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Error deleting file: {e}")


# Create file w/ headers
try:
    with open(filename, "x", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
except FileExistsError:
    pass  # If file exists, skip header writing

try:
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        sensor_value = round(random.uniform(10.0, 100.0), 2)

        # Write 20 rows of fake data
        with open(filename, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            timestamp = datetime.now(timezone.utc).isoformat()


            for _ in range(dataSize):
                sensorValue = round(random.uniform(20.0, 100.0), 2)
                writer.writerow([timestamp, sensorValue])

            
            # Force flushing of the data to disk, this makes python update the file
            csvfile.flush()
            os.fsync(csvfile.fileno())
            
            print(f"Wrote {dataSize} rows")
            time.sleep(updateTime)  # Wait 10 seconds before updating

except KeyboardInterrupt:
    print("Stopped by user.")
