import pandas as pd
from geopy.geocoders import Nominatim
import time

# Loading dataset
df = pd.read_csv("Top Indian Places to Visit.csv")

# Extracting unique cities
cities = df["City"].dropna().unique()

geolocator = Nominatim(user_agent="weekend_getaway_ranker")

city_coordinates = {}

for city in cities:
    try:
        location = geolocator.geocode(f"{city}, India", timeout=10)
        if location:
            city_coordinates[city] = (location.latitude, location.longitude)
        else:
            print(f"Not found: {city}")
    except Exception as e:
        print(f"Error for {city}: {e}")

    time.sleep(1)  # 1 sec time span for API calling

# Save file
import json
with open("city_coordinates.json", "w") as f:
    json.dump(city_coordinates, f, indent=4)

print(f"\nSaved coordinates for {len(city_coordinates)} cities.")
