import telebot
import requests
import re
import json
from datetime import datetime 

# Replace with your bot token and group ID
BOT_TOKEN = "7738466078:AAE2CczVGjy0HZwQVgnKXUx-BI-CN0D-cQ8"
GROUP_ID = -1002601876261  # Replace with your actual group ID
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

# ✅ Function: Fetch vehicle details using new API
def fetch_vehicle_details(plate_number):
    url = "https://api.dhboss.com/apicall/advance_vehicle_verification/"
    payload = {
        "vehicleNo": plate_number,
        "apikeyfill": "Gtbv0iz29bXEJ9CUqFJMMBttsUgkxXWLOMLYxvuIapP6xlLxRuypc5fGOsUkawkCPp6rlU"  # Replace with your actual API key
    }
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        data = response.json().get("response")
        if data:
            return format_vehicle_details(data)
    
    return None  

# ✅ Function: Format vehicle details (Updated for New API)
def format_vehicle_details(data):
    # Current date and time for Last Updated
    last_updated = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # Check if vehicle is financed
    financed_status = "Yes" if data.get("is_financed") else "No"

    return f"""
━━━━━━━━━━━━━━━━━━━━━━
   🚗 VEHICLE DETAILS
━━━━━━━━━━━━━━━━━━━━━━
🔹 Registration Number: {data.get("license_plate", "N/A")}
🔹 Registration Date: {data.get("registration_date", "N/A")}
🔹 Owner Name: {data.get("owner_name", "N/A")}
🔹 Father's Name: {data.get("father_name", "N/A")}
🔹 Present Address: {data.get("present_address", "N/A")}
🔹 Permanent Address: {data.get("permanent_address", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   🚘 VEHICLE SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━
🛠 Brand: {data.get("brand_name", "N/A")}
🚘 Model: {data.get("brand_model", "N/A")}
📌 Class: {data.get("class", "N/A")}
⛽ Fuel Type: {data.get("fuel_type", "N/A")}
📏 Cubic Capacity: {data.get("cubic_capacity", "N/A")} cc
🛞 Seating Capacity: {data.get("seating_capacity", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   ⚙️ TECHNICAL DETAILS
━━━━━━━━━━━━━━━━━━━━━━
🔧 Chassis Number: {data.get("chassis_number", "N/A")}
🔧 Engine Number: {data.get("engine_number", "N/A")}
🚗 Color: {data.get("color", "N/A")}
📜 Norms: {data.get("norms", "N/A")}
⚖ Gross Weight: {data.get("gross_weight", "N/A")}
🔩 Cylinders: {data.get("cylinders", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   📑 REGISTRATION & INSURANCE
━━━━━━━━━━━━━━━━━━━━━━
🛡 Insurance Company: {data.get("insurance_company", "N/A")}
🔖 Policy Number: {data.get("insurance_policy", "N/A")}
📆 Insurance Valid Till: {data.get("insurance_expiry", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   💰 FINANCER DETAILS
━━━━━━━━━━━━━━━━━━━━━━
🏦 Financer: {data.get("financer", "N/A")}
💵 Financed: {financed_status}

━━━━━━━━━━━━━━━━━━━━━━
   📍 OTHER INFORMATION
━━━━━━━━━━━━━━━━━━━━━━
📅 PUCC Valid Upto: {data.get("pucc_upto", "N/A")}
📜 PUCC Number: {data.get("pucc_number", "N/A")}
👥 Owner Count: {data.get("owner_count", "N/A")}
🛑 Tax Paid Upto: {data.get("tax_paid_upto", "N/A")}
🛂 Permit Number: {data.get("permit_number", "N/A")}
📅 Permit Valid Upto: {data.get("permit_valid_upto", "N/A")}
🚛 Permit Type: {data.get("permit_type", "N/A")}
🆔 National Permit Number: {data.get("national_permit_number", "N/A")}
📆 National Permit Valid Upto: {data.get("national_permit_upto", "N/A")}
📌 Vehicle Age: {data.get("vehicle_age", "N/A")}
📜 NOC Details: {data.get("noc_details", "N/A")}
🏢 Permit Issued By: {data.get("national_permit_issued_by", "N/A")}
📅 Permit Issue Date: {data.get("permit_issue_date", "N/A")}
📅 Permit Valid From: {data.get("permit_valid_from", "N/A")}
📅 Tax Upto: {data.get("tax_upto", "N/A")}

━━━━━━━━━━━━━━━━━━━━━━
   📢 STATUS
━━━━━━━━━━━━━━━━━━━━━━
✅ RC Status: {data.get("rc_status", "N/A")}
🕒 Last Updated: {last_updated}

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
        bot.reply_to(message, "❌ This bot works only in https://t.me/+DVC90_599xw3NmE0 group.")
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
