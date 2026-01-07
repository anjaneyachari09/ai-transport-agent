from transport_knowledge import infer_public_transport

def infer_route_traffic(route):
    distance = route["distance_km"]

    # Free-flow driving time at 60 km/h
    expected_time = (distance / 60) * 60
    actual_time = route["driving_duration_min"]

    ratio = actual_time / expected_time

    if ratio > 2:
        level = "heavy"
    elif ratio > 1.3:
        level = "medium"
    else:
        level = "low"

    return {
        "level": level,
        "expected_time": expected_time,
        "actual_time": actual_time,
        "congestion_ratio": ratio
    }



def choose_best_transport(routes, city_name=None):
    distance = routes[0]["distance_km"]

    # Get public transport info (nationwide logic)
    public_transport = infer_public_transport(
        city_name,
        src_coords=routes[0].get("src_coords"),
        dst_coords=routes[0].get("dst_coords")
    )



    # Walking rule
    if distance <= 1:
        return {
            "best_mode": "walking",
            "reason": (
                f"The destination is only {distance:.1f} km away, "
                "so walking is the most efficient option."
            ),
            "public_transport": public_transport
        }

    # Analyze driving route traffic
    driving = next(r for r in routes if r["mode"] == "driving")
    traffic_info = infer_route_traffic(driving)

    # Cycling decision (traffic-aware)
    if traffic_info["level"] in ["heavy", "medium"] and distance <= 7:
        return {
            "best_mode": "cycling",
            "reason": (
                f"The driving route shows {traffic_info['level']} congestion. "
                f"Although the free-flow driving time is "
                f"{traffic_info['expected_time']:.1f} minutes, "
                f"the actual estimated time is "
                f"{traffic_info['actual_time']:.1f} minutes "
                f"({traffic_info['congestion_ratio']:.1f}× slower). "
                f"For a distance of {distance:.1f} km, cycling avoids congestion "
                "and provides a more predictable travel time."
            ),
            "public_transport": public_transport
        }

    # Otherwise choose fastest
    best = min(routes, key=lambda r: r["duration_min"])

    return {
        "best_mode": best["mode"],
        "reason": (
            f"{best['mode'].capitalize()} is recommended because it "
            f"offers the shortest travel time "
            f"({best['duration_min']:.1f} minutes) "
            f"for a distance of {distance:.1f} km."
        ),
        "public_transport": public_transport
    }

