import sqlite3
import telebot
import requests
import re  # Import this at the top

# Bot Token
BOT_TOKEN = "7738466078:AAE2CczVGjy0HZwQVgnKXUx-BI-CN0D-cQ8"
bot = telebot.TeleBot(BOT_TOKEN)

# Allowed Group ID
ALLOWED_GROUP_ID = -1002320210604

# Bot Owner ID
BOT_OWNER_ID = 7394317325

# User search state tracking
user_search_state = {}  # Keeps track of users currently searching

# Database setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Create Table If Not Exists
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    credits INTEGER DEFAULT 60)''')
conn.commit()

# Function to get user credits
def get_user_credits(user_id):
    """Retrieve the user's credit balance from the database."""
    conn = sqlite3.connect("users.db")  # Ensure the database connection is established
    cursor = conn.cursor()  # Always create a new cursor for each query

    cursor.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()  # Close the connection after fetching data

    return result[0] if result else 0  # Return credits or default to 0

# Function to update user credits
def update_credits(user_id, amount):
    cursor.execute("UPDATE users SET credits = ? WHERE user_id=?", (amount, user_id))
    conn.commit()

# Start Command Handler
@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.type == "private" or message.chat.id != ALLOWED_GROUP_ID:
        bot.send_message(message.chat.id, "❌ This bot works only in @RtoVehicle group")
        return
    
    user_id = message.chat.id
    get_user_credits(user_id)  # Ensure user exists
    bot.send_message(message.chat.id, "Welcome! Use the buttons below.", reply_markup=main_menu())

# Function to create main menu buttons
def main_menu():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = telebot.types.KeyboardButton("👤 Profile")
    search_button = telebot.types.KeyboardButton("🔍 Search Details")
    keyboard.add(profile_button, search_button)
    return keyboard

# Profile Command
@bot.message_handler(func=lambda message: message.text == "👤 Profile")
def show_profile(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    user_id = message.from_user.id
    credits = get_user_credits(user_id)

    bot.send_message(
        message.chat.id,
        f"👤 *Your Profile*\n"
        f"💰 Credits: {credits}",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# Dictionary to track user search states
user_search_state = {}

# Search Details Button
@bot.message_handler(func=lambda message: message.text == "🔍 Search Details")
def ask_vehicle_number_for_search(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name

    credits = get_user_credits(user_id)
    if credits < 20:
        keyboard = telebot.types.InlineKeyboardMarkup()
        buy_button = telebot.types.InlineKeyboardButton("💳 Buy Credit", url="https://t.me/bjxxjjhbb")
        keyboard.add(buy_button)
        bot.send_message(message.chat.id, "❌ You have run out of credits!", reply_markup=keyboard)
        return

    user_search_state[user_id] = True  # Track user search state

    bot.send_message(message.chat.id, f"🔍 *{user_name}, enter vehicle number (e.g., GJ01KD1255):*", parse_mode="Markdown")

# Search Vehicle Details
@bot.message_handler(func=lambda message: message.from_user.id in user_search_state)
def fetch_vehicle_details(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    reg_no = message.text.strip()

    if message.chat.id != ALLOWED_GROUP_ID:
        return

    credits = get_user_credits(user_id)
    if credits < 20:
        bot.send_message(message.chat.id, "❌ You don't have enough credits!")
        return

    # Deduct credits and send message with username
    update_credits(user_id, credits - 20)
    bot.send_message(message.chat.id, f"🔍 *{user_name}*, fetching details for *{reg_no}*, please wait...", parse_mode="Markdown")

    details = get_vehicle_details(reg_no)

    if "Vehicle details not found" not in details:
        bot.send_message(message.chat.id, f"🔍 *{user_name}*\n{details}", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"❌ *{user_name}*, vehicle details not found!", parse_mode="Markdown")

    # Remove user from search state
    user_search_state.pop(user_id, None)

def escape_markdown(text):
    """Escape Telegram Markdown special characters."""
    escape_chars = r'_*()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

def get_vehicle_details(reg_no):
    api_url = f"https://carflow-mocha.vercel.app/api/vehicle?numberPlate={reg_no}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if data["statusCode"] == 200:
            v = data["response"]

            message = (
                f"🚗 *Vehicle Information*\n\n"
                f"🔹 *Registration Details*\n"
                f"➤ Registration Number: {v.get('regNo', 'N/A')}\n"
                f"➤ RTO Code: {v.get('rtoCode', 'N/A')}\n"
                f"➤ Registration Authority: {v.get('regAuthority', 'N/A')}\n"
                f"➤ Registration Date: {v.get('regDate', 'N/A')}\n\n"

                f"🔹 *Vehicle Specifications*\n"
                f"➤ Vehicle Class: {v.get('vehicleClass', 'N/A')}\n"
                f"➤ Manufacturer: {v.get('manufacturer', 'N/A')}\n"
                f"➤ Model: {v.get('vehicle', 'N/A')} ({v.get('variant', 'N/A')})\n"
                f"➤ Fuel Type: {v.get('fuelType', 'N/A')}\n"
                f"➤ Cubic Capacity: {v.get('cubicCapacity', 'N/A')} cc\n"
                f"➤ Vehicle Type: {v.get('vehicleType', 'N/A')}\n"
                f"➤ Seat Capacity: {v.get('seatCapacity', 'N/A')}\n"
                f"➤ Commercial Vehicle: {'Yes' if v.get('isCommercial') else 'No'}\n\n"

                f"🔹 *Owner Information*\n"
                f"➤ Owner Name: {v.get('owner', 'N/A')}\n"
                f"➤ Father's Name: {v.get('ownerFatherName', 'N/A')}\n"
                f"➤ Permanent Address: {v.get('permAddress', 'N/A')}\n"
                f"➤ Pincode: {v.get('pincode', 'N/A')}\n\n"

                f"🔹 *Financial & Insurance Details*\n"
                f"➤ Financer Name: {v.get('financerName', 'N/A')}\n"
                f"➤ Insurance Company: {v.get('insuranceCompanyName', 'N/A')}\n"
                f"➤ Insurance Validity: {v.get('insuranceUpto', 'N/A')}\n"
                f"➤ Insurance Expired: {'Yes' if v.get('insuranceExpired') else 'No'}\n\n"

                f"🔹 *PUC Details*\n"
                f"➤ PUCC Number: {v.get('puccNumber', 'N/A')}\n"
                f"➤ PUCC Validity: {v.get('puccValidUpto', 'N/A')}\n\n"

                f"🔹 *Additional Information*\n"
                f"➤ Chassis Number: {v.get('chassis', 'N/A')}\n"
                f"➤ Engine Number: {v.get('engine', 'N/A')}\n"
                f"➤ Data Status: {v.get('dataStatus', 'N/A')}\n"
                f"➤ Last Updated: {v.get('lmDate', 'N/A')}\n\n"

                f"⭒ Powered By: @VEHICLEINFOIND_BOT"
            )

            return escape_markdown(message)  # ✅ Use the escape function
        else:
            return "❌ Vehicle Not Found!"
    else:
        return "❌ API Error! Try again later."
        
# Add Credits Command (Only for Bot Owner)
@bot.message_handler(commands=['addcredits'])
def add_credits(message):
    if message.from_user.id != BOT_OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command!")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "⚠️ Usage: `/addcredits <user_id> <amount>`", parse_mode="Markdown")
            return

        user_id = int(command_parts[1])
        amount = int(command_parts[2])

        current_credits = get_user_credits(user_id)
        update_credits(user_id, current_credits + amount)

        bot.reply_to(message, f"✅ Added {amount} credits to user {user_id}.\nTotal Credits: {current_credits + amount}")

    except ValueError:
        bot.reply_to(message, "❌ Invalid format! Use `/addcredits <user_id> <amount>`", parse_mode="Markdown")

# Start polling
print("Bot is running...")
bot.polling(none_stop=True)
