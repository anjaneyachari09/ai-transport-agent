from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from maps import get_coordinates, get_route
from agent import choose_best_transport

app = Flask(__name__)

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()

    if "->" not in incoming_msg:
        resp = MessagingResponse()
        resp.message("❌ Use format:\nSOURCE -> DESTINATION")
        return str(resp)

    source, destination = map(str.strip, incoming_msg.split("->"))

    src_coords = get_coordinates(source)
    dst_coords = get_coordinates(destination)

    if not src_coords or not dst_coords:
        resp = MessagingResponse()
        resp.message("❌ Could not find one of the locations.")
        return str(resp)

    routes = []
    for mode in ["driving", "walking", "cycling"]:
        routes.append(get_route(src_coords, dst_coords, mode))

    decision = choose_best_transport(routes, city_name=source.split()[-1])

    reply = f"🚦 Transport Recommendation\n{decision['reason']}\n\n"

    pt = decision.get("public_transport", {})
    if pt.get("available") is True:
        reply += f"🚌 Public Transport: {pt['mode']} available"
    elif pt.get("available") is None:
        reply += "🚌 Public Transport: Unable to verify currently"
    else:
        reply += "🚌 Public Transport: Not available"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
