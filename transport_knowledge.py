import requests
import math


# -----------------------------------------
# OSM Bus Stop Detection using Overpass API
# -----------------------------------------
def osm_bus_stops_nearby(lat, lon, radius=1500):
    """
    Checks if bus stops exist within `radius` meters
    using OpenStreetMap Overpass API.

    Returns:
    - True  → bus stops found
    - False → checked, but none found
    - None  → could not verify (server busy / timeout)
    """

    query = f"""
    [out:json][timeout:25];
    (
      node["highway"="bus_stop"](around:{radius},{lat},{lon});
      node["amenity"="bus_station"](around:{radius},{lat},{lon});
      node["public_transport"="platform"](around:{radius},{lat},{lon});
      way["highway"="platform"](around:{radius},{lat},{lon});
    );
    out body;
    """

    headers = {
        "User-Agent": "AI-Transport-Agent/1.0 (educational project)"
    }

    try:
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers=headers,
            timeout=30
        )
        data = response.json()
        return len(data.get("elements", [])) > 0

    except Exception:
        # Overpass is busy or unreachable
        return None


# --------------------------------------------------
# PUBLIC TRANSPORT AVAILABILITY (INFRASTRUCTURE-BASED)
# --------------------------------------------------
def infer_public_transport(city_name, src_coords=None, dst_coords=None):
    """
    Determines public transport availability using REAL infrastructure,
    not distance guessing.
    """

    if not src_coords or not dst_coords:
        return {
            "available": False,
            "mode": None,
            "source": None,
            "reason": "Insufficient location data to verify public transport."
        }

    src_lat, src_lon = src_coords
    dst_lat, dst_lon = dst_coords

    bus_near_source = osm_bus_stops_nearby(src_lat, src_lon)
    bus_near_destination = osm_bus_stops_nearby(dst_lat, dst_lon)

    # Case 1: Could not verify (Overpass busy)
    if bus_near_source is None or bus_near_destination is None:
        return {
            "available": None,
            "mode": None,
            "source": "OpenStreetMap (Overpass API)",
            "reason": (
                "Public transport availability could not be verified at the moment "
                "due to temporary map service limitations."
            )
        }

    # Case 2: Bus infrastructure found
    if bus_near_source or bus_near_destination:
        return {
            "available": True,
            "mode": "bus",
            "source": "OpenStreetMap (bus stop proximity)",
            "reason": (
                "Verified bus stop infrastructure exists near the source or "
                "destination, indicating public bus service availability."
            )
        }

    # Case 3: Verified absence
    return {
        "available": False,
        "mode": None,
        "source": None,
        "reason": (
            "No verified bus stop infrastructure was found near the source "
            "or destination using OpenStreetMap data."
        )
    }



