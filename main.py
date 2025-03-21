import telebot
import requests
import re
import json
import time

# Replace with your bot token and group ID
BOT_TOKEN = "7932561618:AAEm_srwvZ0F6JuVBzpr0WzLEdktBzbT4Ko"
GROUP_ID = -1002508827258  # Replace with your actual group ID
CHANNEL_USERNAME = "@BOTS_OSINTT"  # Aapka channel username
ADMIN_CHAT_ID = 7394317325  # Yahan apna Telegram ID daalein

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Function: Check if user is a member of the channel
def is_member(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False  

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
🔹 Registration Authority: {data.get("regAuthority", "N/A")}
🔹 Registration Date: {data.get("regDate", "N/A")}
🔹 Owner Name: {data.get("owner", "N/A")}
🔹 Father's Name: {data.get("ownerFatherName", "N/A")}
🔹 Address: {data.get("presentAddress", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   🚘 VEHICLE SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━
🛠 Manufacturer: {data.get("manufacturer", "N/A")}
🚘 Model: {data.get("vehicle", "N/A")}
📌 Variant: {data.get("variant", "N/A")}
⛽ Fuel Type: {data.get("fuelType", "N/A")}
🪑 Seat Capacity: {data.get("seatCapacity", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   ⚙️ TECHNICAL DETAILS
━━━━━━━━━━━━━━━━━━━━━━
🔧 Chassis Number: {data.get("chassis", "N/A")}
🔧 Engine Number: {data.get("engine", "N/A")}
📏 Cubic Capacity: {data.get("cubicCapacity", "N/A")} cc

━━━━━━━━━━━━━━━━━━━━━━
   📑 REGISTRATION & INSURANCE
━━━━━━━━━━━━━━━━━━━━━━
🛡 Insurance Company: {data.get("insuranceCompanyName", "N/A")}
🔖 Policy Number: {data.get("insurancePolicyNumber", "N/A")}
📆 Insurance Valid Till: {data.get("insuranceUpto", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   💰 FINANCER DETAILS
━━━━━━━━━━━━━━━━━━━━━━
🏦 Financer: {data.get("financerName", "N/A")}
💵 Financed: {financed_status}

━━━━━━━━━━━━━━━━━━━━━━
   📍 OTHER INFORMATION
━━━━━━━━━━━━━━━━━━━━━━
🏭 Manufacturing Year: {data.get("manufacturerYear", "N/A")}
📌 Pincode: {data.get("pincode", "N/A")}
🕒 Last Updated: {data.get("lmDate", "N/A")}
📅 Data Status: {data.get("dataStatus", "N/A")}
🛞 Vehicle Type: {data.get("vehicleType", "N/A")}
🏢 RTO Code: {data.get("rtoCode", "N/A")}
📅 Emission Date: {data.get("eDate", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   📢 STATUS
━━━━━━━━━━━━━━━━━━━━━━
✅ RC Status: Y
🕒 Last Updated: {data.get("lmDate", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
⭒ Powered By: @VEHICLEINFOIND_BOT
━━━━━━━━━━━━━━━━━━━━━━
"""

# ✅ Load & Save Users List
USER_DATA_FILE = "users.json"

def load_users():
    try:
        with open(USER_DATA_FILE, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file)

# ✅ /start command
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    users = load_users()

    if chat_id not in users:
        users.append(chat_id)
        save_users(users)

    if message.chat.type == "private":
        bot.reply_to(message, "❌ This bot works only in @RtoVehicle group.")
    else:
        bot.reply_to(message, "Send a vehicle number to get details.")

# ✅ Broadcast Command (Only for Admin)
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.reply_to(message, "❌ You are not authorized to send broadcasts.")
        return

    text = message.text.replace("/broadcast ", "").strip()
    users = load_users()

    if not users:
        bot.reply_to(message, "⚠️ No users found to broadcast.")
        return

    bot.reply_to(message, f"📢 Sending broadcast to {len(users)} users...")

    failed = 0
    for user_id in users:
        try:
            bot.send_message(user_id, f"📢 Broadcast:\n{text}")
            time.sleep(1)
        except Exception as e:
            failed += 1
            print(f"❌ Failed to send message to {user_id}: {e}")

    bot.reply_to(message, f"✅ Broadcast sent! ({len(users) - failed} success, {failed} failed)")

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
        bot.reply_to(message, "🚨 Join the channel first to use this bot!", reply_markup=keyboard)
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
