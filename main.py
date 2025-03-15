import telebot
import requests
import re

# Replace with your bot token and group ID
BOT_TOKEN = "7738466078:AAE2CczVGjy0HZwQVgnKXUx-BI-CN0D-cQ8"
GROUP_ID = -1002320210604  # Replace with your actual group ID
CHANNEL_USERNAME = "@BOTS_OSINTT"  # Aapka channel username

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Function: Check if user is a member of the channel
def is_member(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False  # Agar koi error aaye toh assume karenge ki user member nahi hai

# ✅ Function: Fetch vehicle details
def fetch_vehicle_details(plate_number):
    url = f"https://carflow-mocha.vercel.app/api/vehicle?numberPlate={plate_number}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get("response")
        if data:  
            return format_vehicle_details(data)
    
    return None  

# ✅ Function: Format vehicle details
def format_vehicle_details(data):
    financed_status = "Yes" if data.get("financerName") and data["financerName"].lower() != "on cash" else "No"

    return f"""
━━━━━━━━━━━━━━━━━━━━━━
   🚗 VEHICLE DETAILS
━━━━━━━━━━━━━━━━━━━━━━
🔹 Registration Number: {data.get("regNo", "N/A")}
🔹 Owner Name: {data.get("owner", "N/A")}
🔹 Address: {data.get("presentAddress", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   🚘 VEHICLE SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━
🛠 Manufacturer: {data.get("manufacturer", "N/A")}
🚘 Model: {data.get("vehicle", "N/A")}
⛽ Fuel Type: {data.get("fuelType", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   📢 STATUS
━━━━━━━━━━━━━━━━━━━━━━
✅ RC Status: Y
🕒 Last Updated: {data.get("lmDate", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
⭒ Powered By: @VEHICLEINFOIND_BOT
━━━━━━━━━━━━━━━━━━━━━━
"""

# ✅ /start command
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == "private":
        bot.reply_to(message, "❌ This bot works only in @RtoVehicle group.")
    else:
        bot.reply_to(message, "Send a vehicle number to get details.")

# ✅ Message handler: Check membership and fetch vehicle details
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.id != GROUP_ID:
        return  

    user_id = message.from_user.id

    # 🔍 Check if user is a member of the channel
    if not is_member(user_id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        join_button = telebot.types.InlineKeyboardButton("JOIN CHANNEL ✅", url="https://t.me/BOTS_OSINTT")
        keyboard.add(join_button)
        bot.reply_to(message, "🚨 **Join the channel first to use this bot!**", reply_markup=keyboard)
        return

    # 🔍 Validate vehicle number (max 10 characters, no spaces)
    plate_number = message.text.strip().upper()
    if not re.match(r"^[A-Z0-9]{1,10}$", plate_number):
        return  

    # 🔍 Fetch vehicle details
    details = fetch_vehicle_details(plate_number)
    
    if details:
        bot.reply_to(message, details)
    else:
        bot.reply_to(message, "❌ No details found for this vehicle number.")

# ✅ Run the bot
bot.polling()
