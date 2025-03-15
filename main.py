from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests

# Bot Token, Group ID & Channel Username
BOT_TOKEN = "7738466078:AAE2CczVGjy0HZwQVgnKXUx-BI-CN0D-cQ8"
GROUP_USERNAME = "@RtoVehicle"
CHANNEL_USERNAME = "@BOTS_OSINTT"

def is_member(user_id, context):
    try:
        chat_member = context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

def is_in_group(update: Update):
    return update.message.chat.username == GROUP_USERNAME or str(update.message.chat.id).startswith("-100")

def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Check if used outside the group
    if not is_in_group(update):
        update.message.reply_text("❌ This bot works only in @RtoVehicle group.")
        return

    # Check if user has joined the required channel
    if not is_member(user_id, context):
        keyboard = [[InlineKeyboardButton("JOIN CHANNEL✅", url="https://t.me/BOTS_OSINTT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Please join the channel first before using this bot.", reply_markup=reply_markup)
        return

    update.message.reply_text("Welcome! Send a vehicle number to search.")

def fetch_vehicle_details(vehicle_number):
    if " " in vehicle_number or len(vehicle_number) > 10:
        return None  # Invalid format, ignore

    url = f"https://car.app/api/vehicle?numberPlate={vehicle_number}"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get("response"):
        data = response.json()["response"]

        # Check financing status
        financer_name = data.get("financerName", "N/A")
        financed_status = "Yes" if financer_name and financer_name != "On Cash" else "No"

        # Format vehicle details
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

def search_vehicle(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # If bot is used outside the group
    if not is_in_group(update):
        update.message.reply_text("❌ This bot works only in @RtoVehicle group.")
        return

    # If user hasn't joined the required channel
    if not is_member(user_id, context):
        keyboard = [[InlineKeyboardButton("JOIN CHANNEL✅", url="https://t.me/BOTS_OSINTT")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Please join the channel first before using this bot.", reply_markup=reply_markup)
        return

    vehicle_number = update.message.text.strip().upper()
    details = fetch_vehicle_details(vehicle_number)

    if details:
        update.message.reply_text(details, parse_mode="Markdown")
    else:
        update.message.reply_text("No details found or invalid vehicle number.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search_vehicle))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
