from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

from telegram.request import HTTPXRequest

from maps import get_coordinates, get_route
from agent import choose_best_transport



TOKEN = "8590133057:AAGQmdlbKSqmXRNz7j413Rz3S8dg3xMEXM8"



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to Smart Transport Advisor Bot 🤖*\n\n"
        "I help you choose the best way to travel between two places using:\n"
        "• OpenStreetMap data\n"
        "• Traffic-aware route analysis\n"
        "• Public transport detection (bus/metro where available)\n\n"
        "🧭 *HOW IT WORKS:*\n"
        "1️⃣ Send a route in this format:\n"
        "   `Source → Destination`\n\n"
        "2️⃣ I calculate:\n"
        "   🚗 Driving time (traffic-aware)\n"
        "   🚶 Walking time\n"
        "   🚲 Cycling time\n\n"
        "3️⃣ I analyze congestion & distance\n"
        "4️⃣ I recommend the best option\n"
        "5️⃣ I check public transport availability\n\n"
        "Send a route to begin 🚀",
        parse_mode="Markdown"
    )



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    source = destination = None


    if "->" in text:
        source, destination = map(str.strip, text.split("->", 1))

    elif " to " in text:
        source, destination = map(str.strip, text.split(" to ", 1))

    elif text.startswith("from ") and " to " in text:
        text = text.replace("from ", "", 1)
        source, destination = map(str.strip, text.split(" to ", 1))


    if not source or not destination:
        await update.message.reply_text(
            "❌ I couldn't understand the route.\n\n"
            "Try one of these formats:\n"
            "• Miyapur → Gandimaisamma\n"
            "• Miyapur to Gandimaisamma\n"
            "• from Miyapur to Gandimaisamma"
        )
        return


    src_coords = get_coordinates(source)
    dst_coords = get_coordinates(destination)

    if not src_coords or not dst_coords:
        await update.message.reply_text(
            "❌ Could not find one of the locations.\n"
            "Please try a clearer place name."
        )
        return


    routes = []
    for mode in ["driving", "walking", "cycling"]:
        routes.append(get_route(src_coords, dst_coords, mode))


    decision = choose_best_transport(
        routes,
        city_name=source.split()[-1]
    )

 
    reply = (
        "🚦 *Transport Recommendation*\n\n"
        f"{decision['reason']}\n\n"
    )

    pt = decision.get("public_transport", {})
    if pt.get("available") is True:
        reply += f"🚌 *Public Transport:* {pt['mode']} available"
    elif pt.get("available") is None:
        reply += "🚌 *Public Transport:* Availability could not be verified"
    else:
        reply += "🚌 *Public Transport:* Not available"

    await update.message.reply_text(reply, parse_mode="Markdown")



def main():
    request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=30
    )

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .request(request)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram bot is running...")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message"]
    )



if __name__ == "__main__":
    main()
