from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Bot Token, Group ID & Channel Username
BOT_TOKEN = "7738466078:AAE2CczVGjy0HZwQVgnKXUx-BI-CN0D-cQ8"
GROUP_ID = -1002320210604  # Aapke group ka ID
CHANNEL_USERNAME = "@BOTS_OSINTT"

async def is_member(user_id, application):
    try:
        chat_member = await application.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if chat_id != GROUP_ID:  # Agar group ke bahar hai
        await update.message.reply_text("❌ This bot works only in @RtoVehicle group.")
        return

    # Check if user is a member of the channel
    if not await is_member(user_id, context.application):
        keyboard = [[InlineKeyboardButton("JOIN CHANNEL✅", url="https://t.me/BOTS_OSINTT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please join the channel first before using this bot.", reply_markup=reply_markup)
        return

    await update.message.reply_text("Welcome! Send a vehicle number to search.")

async def fetch_vehicle_details(vehicle_number):
    if " " in vehicle_number or len(vehicle_number) > 10:
        return None  # Invalid format, ignore

    url = f"https://car.app/api/vehicle?numberPlate={vehicle_number}"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get("response"):
        data = response.json()["response"]
        financer_name = data.get("financerName", "N/A")
        financed_status = "Yes" if financer_name and financer_name != "On Cash" else "No"

        message = f"""
━━━━━━━━━━━━━━━━━━━━━━  
   🚗 **VEHICLE DETAILS**  
━━━━━━━━━━━━━━━━━━━━━━  
🔹 **Registration Number:** {data.get("regNo", "N/A")}  
🔹 **Registration Authority:** {data.get("regAuthority", "N/A")}  
🔹 **Registration Date:** {data.get("regDate", "N/A")}  
🔹 **Owner Name:** {data.get("owner", "N/A")}  
🔹 **Father's Name:** {data.get("ownerFatherName", "N/A")}  
🔹 **Address:** {data.get("presentAddress", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  
   🚘 **VEHICLE SPECIFICATIONS**  
━━━━━━━━━━━━━━━━━━━━━━  
🛠 **Manufacturer:** {data.get("manufacturer", "N/A")}  
🚘 **Model:** {data.get("vehicle", "N/A")}  
📌 **Variant:** {data.get("variant", "N/A")}  
⛽ **Fuel Type:** {data.get("fuelType", "N/A")}  
🪑 **Seat Capacity:** {data.get("seatCapacity", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  
   ⚙️ **TECHNICAL DETAILS**  
━━━━━━━━━━━━━━━━━━━━━━  
🔧 **Chassis Number:** {data.get("chassis", "N/A")}  
🔧 **Engine Number:** {data.get("engine", "N/A")}  
📏 **Cubic Capacity:** {data.get("cubicCapacity", "N/A")} cc  

━━━━━━━━━━━━━━━━━━━━━━  
   📑 **REGISTRATION & INSURANCE**  
━━━━━━━━━━━━━━━━━━━━━━  
🛡 **Insurance Company:** {data.get("insuranceCompanyName", "N/A")}  
🔖 **Policy Number:** {data.get("insurancePolicyNumber", "N/A")}  
📆 **Insurance Valid Till:** {data.get("insuranceUpto", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  
   💰 **FINANCER DETAILS**  
━━━━━━━━━━━━━━━━━━━━━━  
🏦 **Financer:** {data.get("financerName", "N/A")}  
💵 **Financed:** {financed_status}  

━━━━━━━━━━━━━━━━━━━━━━  
   📍 **OTHER INFORMATION**  
━━━━━━━━━━━━━━━━━━━━━━  
🏭 **Manufacturing Year:** {data.get("manufacturerYear", "N/A")}  
📌 **Pincode:** {data.get("pincode", "N/A")}  
🕒 **Last Updated:** {data.get("lmDate", "N/A")}  
📅 **Data Status:** {data.get("dataStatus", "N/A")}  
🛞 **Vehicle Type:** {data.get("vehicleType", "N/A")}  
🏢 **RTO Code:** {data.get("rtoCode", "N/A")}  
📅 **Emission Date:** {data.get("eDate", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  
   📢 **STATUS**  
━━━━━━━━━━━━━━━━━━━━━━  
✅ **RC Status:** Y  
🕒 **Last Updated:** {data.get("lmDate", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  
⭒ **Powered By:** @VEHICLEINFOIND_BOT  
━━━━━━━━━━━━━━━━━━━━━━  
"""
        return message
    else:
        return "No details found for this vehicle number."

async def search_vehicle(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if chat_id != GROUP_ID:  # Agar group ke bahar hai
        await update.message.reply_text("❌ This bot works only in @RtoVehicle group.")
        return

    if not await is_member(user_id, context.application):
        keyboard = [[InlineKeyboardButton("JOIN CHANNEL✅", url="https://t.me/BOTS_OSINTT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please join the channel first before using this bot.", reply_markup=reply_markup)
        return

    vehicle_number = update.message.text.strip().upper()
    details = await fetch_vehicle_details(vehicle_number)

    if details:
        await update.message.reply_text(details)
    else:
        await update.message.reply_text("No details found or invalid vehicle number.")

async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_vehicle))

    print("Bot is running...")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
