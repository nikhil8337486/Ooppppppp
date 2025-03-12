import telebot
import requests

# Bot Token
BOT_TOKEN = "7738466078:AAEej3cy8A1y8edGsR8tb6uuucSc8FWxAt8"
bot = telebot.TeleBot(BOT_TOKEN)

# Allowed Group ID
ALLOWED_GROUP_ID = -1002320210604  # @RtoVehicle group ID

# Bot Owner ID
BOT_OWNER_ID = 7394317325  

# User ke credits store karne ke liye
user_credits = {}

# Reply Keyboard Markup (Buttons)
def main_menu():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("👤 Profile", "🔍 Search Details")
    return keyboard

# Start Command Handler
@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.type == "private" or message.chat.id != ALLOWED_GROUP_ID:
        bot.send_message(message.chat.id, "❌ This bot works only in @RtoVehicle group!")
        return
    bot.send_message(message.chat.id, "✅ Bot is active in @RtoVehicle group!", reply_markup=main_menu())

# Welcome Message for New Members
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    for new_user in message.new_chat_members:
        user_id = new_user.id
        first_name = new_user.first_name

        if user_id not in user_credits:
            user_credits[user_id] = 60  

        bot.send_message(
            message.chat.id,
            f"🎉 Welcome, {first_name}! 🚀\n\n"
            "You have *60 credits* (3 free searches).",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

# Profile Command
@bot.message_handler(func=lambda message: message.text == "👤 Profile")
def show_profile(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    user_id = message.from_user.id
    if user_id not in user_credits:
        user_credits[user_id] = 60  

    credits = user_credits.get(user_id, 0)

    bot.send_message(
        message.chat.id,
        f"👤 *Your Profile*\n"
        f"💰 Credits: {credits}",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# Search Details Button
@bot.message_handler(func=lambda message: message.text == "🔍 Search Details")
def ask_vehicle_number_for_search(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    bot.send_message(message.chat.id, "🚘 Enter vehicle number (e.g., GJ01KD1255):")
    bot.register_next_step_handler(message, fetch_vehicle_info)

# Fetch Vehicle Info
def fetch_vehicle_info(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    if not message.text:  # Agar text None hai ya empty hai toh error se bacha sakte hain
        bot.send_message(message.chat.id, "❌ Please send a valid vehicle number!")
        return

    user_id = message.from_user.id

    if user_id not in user_credits:
        user_credits[user_id] = 60  

    if user_credits[user_id] < 20:
        keyboard = telebot.types.InlineKeyboardMarkup()
        buy_button = telebot.types.InlineKeyboardButton("💳 Buy Credit", url="https://t.me/bjxxjjhbb")
        keyboard.add(buy_button)

        bot.send_message(message.chat.id, "❌ You have run out of credits!", reply_markup=keyboard)
        return

    reg_no = message.text.strip().upper()
    bot.send_message(message.chat.id, "🔍 Fetching details, please wait...")

    details = get_vehicle_details(reg_no)

    user_credits[user_id] -= 20  # Deduct 20 credits per search
    bot.send_message(message.chat.id, details, reply_markup=main_menu())

# Owner can add credits
@bot.message_handler(commands=['addcredits'])
def add_credits(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    if message.from_user.id != BOT_OWNER_ID:
        bot.send_message(message.chat.id, "❌ You are not authorized to use this command!")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.send_message(message.chat.id, "❌ Usage: /addcredits <user_id> <amount>")
            return

        user_id = int(command_parts[1])
        amount = int(command_parts[2])

        if user_id not in user_credits:
            user_credits[user_id] = 60  

        user_credits[user_id] += amount
        bot.send_message(message.chat.id, f"✅ Successfully added {amount} credits to user {user_id}!", reply_markup=main_menu())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid command format! Use: /addcredits <user_id> <amount>")

# Vehicle details fetch function
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
            return message
        else:
            return "❌ Vehicle details not found!"
    else:
        return "❌ API Error! Try again later."

# Start Bot
print("Bot is running...")
bot.polling(non_stop=True, timeout=60, long_polling_timeout=60)
