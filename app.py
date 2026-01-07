from maps import get_coordinates, get_route
from agent import choose_best_transport



def extract_city(location_text):
    return location_text.split()[-1]


def main():
    source = input("Enter source location: ")
    destination = input("Enter destination location: ")

    src_coords = get_coordinates(source)
    dst_coords = get_coordinates(destination)

    if not src_coords or not dst_coords:
        print("❌ Unable to find locations.")
        return

    modes = ["driving", "walking", "cycling"]
    routes = []

    for mode in modes:
        routes.append(get_route(src_coords, dst_coords, mode))

    # ✅ Use extract_city here
    city = extract_city(source)
    decision = choose_best_transport(routes, city)

    print("\n📊 Route Options:")
    for r in routes:
        print(
            f"{r['mode']:>8} → "
            f"{r['distance_km']:.1f} km, "
            f"{r['duration_min']:.1f} min"
        )

    print("\n🤖 AI Recommendation:")
    print(decision["reason"])

    pt = decision.get("public_transport", {})

    print("\n🚌 Public Transport:")

    if pt.get("available") is True:
        print(f"{pt['mode']} available (source: {pt['source']}).")

    elif pt.get("available") is None:
        print("Availability could not be verified at the moment.")

    else:
        print("Not available for this route.")



if __name__ == "__main__":
    main()
