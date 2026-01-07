import requests

HEADERS = {
    "User-Agent": "AI-Transport-Agent"
}

def get_coordinates(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json"}
    res = requests.get(url, params=params, headers=HEADERS).json()

    if not res:
        return None

    return float(res[0]["lat"]), float(res[0]["lon"])


def get_route(source, destination, mode="driving"):
    src_lat, src_lon = source
    dst_lat, dst_lon = destination

    # OSRM gives realistic duration ONLY for driving
    url = f"http://router.project-osrm.org/route/v1/driving/{src_lon},{src_lat};{dst_lon},{dst_lat}"
    res = requests.get(url, params={"overview": "false"}).json()
    route = res["routes"][0]

    distance_km = route["distance"] / 1000
    driving_duration_min = route["duration"] / 60

    # AI-estimated speeds
    speeds = {
        "walking": 5,
        "cycling": 15,
        "driving": 60
    }

    if mode == "driving":
        duration_min = driving_duration_min
    else:
        duration_min = (distance_km / speeds[mode]) * 60

    return {
        "mode": mode,
        "distance_km": distance_km,
        "duration_min": duration_min,
        "driving_duration_min": driving_duration_min,
        "src_coords": source,
        "dst_coords": destination
    }

