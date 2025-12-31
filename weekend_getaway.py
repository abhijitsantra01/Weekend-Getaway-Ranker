import pandas as pd
import json
from math import radians, sin, cos, sqrt, atan2

# Haversine Distance (km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# Normalization
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())


# Weekend Getaway Ranker
def rank_weekend_getaways(
    source_city="Bangalore",
    top_n=5
):
    # Loading dataset
    df = pd.read_csv("Top Indian Places to Visit.csv")

    # Drop unnecessary index column
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    # Rename columns for easier access
    df.rename(columns={
        "Google review rating": "rating",
        "Number of google review in lakhs": "popularity"
    }, inplace=True)

    #Source_zone determination
    source_zone_series = df.loc[
        df["City"].str.lower() == source_city.lower(), "Zone"
    ]

    if source_zone_series.empty:
        raise ValueError(
            f"Source city '{source_city}' not found in dataset for zone inference"
        )

    source_zone = source_zone_series.iloc[0]

    # Load city coordinates JSON
    with open("city_coordinates.json") as f:
        city_coordinates = json.load(f)

    if source_city not in city_coordinates:
        raise ValueError("Source city not found in city_coordinates.json")

    src_lat, src_lon = city_coordinates[source_city] 

    # Calculate distance using city coordinates
    def calculate_distance(row):
        city = row["City"]
        if city in city_coordinates:
            lat, lon = city_coordinates[city]
            return haversine(src_lat, src_lon, lat, lon)
        else:
            return None

    df["distance_km"] = df.apply(calculate_distance, axis=1)

    # Remove rows where distance couldn't be calculated
    df.dropna(subset=["distance_km"], inplace=True)



    # Zone bonus
    df["zone_bonus"] = df["Zone"].apply(
        lambda z: 1 if z == source_zone else 0
    )

    # Distance witnin 500km range
    MAX_DISTANCE_KM = 500
    df = df[df["distance_km"] <= MAX_DISTANCE_KM]

    # Normalization AFTER filtering
    df["norm_rating"] = normalize(df["rating"])
    df["norm_popularity"] = normalize(df["popularity"])
    df["norm_distance"] = normalize(df["distance_km"])


    # Final score
    df["score"] = (
        0.40 * df["norm_rating"]
        + 0.25 * df["norm_popularity"]
        + 0.30 * (1 - df["norm_distance"])
        + 0.05 * df["zone_bonus"]
    )

    # Remove same-city results
    df = df[df["City"].str.lower() != source_city.lower()]

    # Sort & pick top N
    top = df.sort_values("score", ascending=False).head(top_n)

    # Output
    print(f"Source City: {source_city} ({source_zone} India)\n")

    for i, row in enumerate(top.itertuples(index=False), 1):
        print(
            f"{i}. {row.Name} ({row.State}) | "
            f"City: {row.City} | "
            f"Zone: {row.Zone} | "
            f"Distance: {row.distance_km:.0f} km | "
            f"Score: {row.score:.2f}"
        )

        # Weekly Off days only if available
        if pd.notna(row._asdict().get("Weekly Off")):
            print(f"Weekly Off: {row._asdict().get('Weekly Off')}")



if __name__ == "__main__":
    rank_weekend_getaways(
        source_city="Kolkata",
        top_n=5
    )
