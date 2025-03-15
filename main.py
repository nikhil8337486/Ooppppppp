from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import asyncio
import signal

# 🔑 Bot Token & Group ID
BOT_TOKEN = "YOUR_BOT_TOKEN"
GROUP_ID = -1001234567890  # Aapke group ka ID

# ✅ Function: Start Command
async def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id != GROUP_ID:
        await update.message.reply_text("❌ This bot works only in @RtoVehicle group.")
        return
    await update.message.reply_text("Welcome! Send a vehicle number to search.")

# ✅ Function: Fetch vehicle details
async def fetch_vehicle_details(vehicle_number):
    if " " in vehicle_number or len(vehicle_number) > 10:
        return None

    url = f"https://car.app/api/vehicle?numberPlate={vehicle_number}"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get("response"):
        data = response.json()["response"]
        return f"🚗 **Vehicle:** {data.get('vehicle', 'N/A')}\n🔹 **Owner:** {data.get('owner', 'N/A')}"
    return "No details found for this vehicle number."

# ✅ Function: Search vehicle
async def search_vehicle(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id != GROUP_ID:
        await update.message.reply_text("❌ This bot works only in @RtoVehicle group.")
        return

    vehicle_number = update.message.text.strip().upper()
    details = await fetch_vehicle_details(vehicle_number)

    if details:
        await update.message.reply_text(details)
    else:
        await update.message.reply_text("No details found or invalid vehicle number.")

# ✅ Main function (Fixed asyncio issue)
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_vehicle))

    loop = asyncio.new_event_loop()  # ✅ Fix: Create a new asyncio loop
    asyncio.set_event_loop(loop)

    # ✅ Fix: Handle signals manually
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(application.stop()))

    print("🚀 Bot is running...")
    loop.run_until_complete(application.run_polling())

if __name__ == "__main__":
    main()  # ✅ No `asyncio.run()`, Fixed `add_signal_handler`
