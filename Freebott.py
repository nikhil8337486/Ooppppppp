import telebot
import requests

# Bot ka token
BOT_TOKEN = "7738466078:AAH2qHH0PZBLFompWoQBdf7jtpn2XTvRnJI"
bot = telebot.TeleBot(BOT_TOKEN)

# Sirf is group me bot kaam karega
ALLOWED_GROUP_ID = -1002320210604

# Bot owner ka Telegram ID
BOT_OWNER_ID = 7394317325  # Apna Telegram ID yahan daalo

# User credits store karne ke liye dictionary
user_credits = {}

# Function jo vehicle details fetch karega
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

# Start command
@bot.message_handler(commands=['start'])
def ask_vehicle_number(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        bot.send_message(message.chat.id, "❌ This bot works only in @RtoVehicle group!")
        return

    user_id = message.from_user.id
    if user_id not in user_credits:
        user_credits[user_id] = 40  # 2 free searches (20x2 = 40 credits)

    bot.send_message(
        message.chat.id,
        "🚘 *Welcome!*\nYou have *2 free searches.*\nPlease enter your vehicle number (e.g., GJ01kd1255):"
    )
    bot.register_next_step_handler(message, fetch_vehicle_info)

# Vehicle details fetch karega
def fetch_vehicle_info(message):
    user_id = message.from_user.id

    if user_id not in user_credits or user_credits[user_id] < 20:
        bot.send_message(message.chat.id, "❌ You have run out of credits! Earn more by referring friends.")
        send_referral_options(message.chat.id, user_id)
        return

    reg_no = message.text.strip().upper()
    bot.send_message(message.chat.id, "🔍 Fetching details, please wait...")

    details = get_vehicle_details(reg_no)

    user_credits[user_id] -= 20  # 20 credit cut honge
    bot.send_message(message.chat.id, details)

# Referral ka option show karega
def send_referral_options(chat_id, user_id):
    referral_message = (
        "🎉 You have run out of credits!\n"
        "🆓 Earn 20 credits for each referral.\n"
        "📤 Invite your friends to continue searching for vehicle details."
    )

    keyboard = telebot.types.InlineKeyboardMarkup()
    referral_button = telebot.types.InlineKeyboardButton(text="🔗 Refer & Earn", url="https://t.me/VEHICLEINFOIND_BOT?start=referral")
    keyboard.add(referral_button)

    bot.send_message(chat_id, referral_message, reply_markup=keyboard)

# Bot owner ke liye credit add karne ka command
@bot.message_handler(commands=['addcredits'])
def add_credits(message):
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
            user_credits[user_id] = 0

        user_credits[user_id] += amount
        bot.send_message(message.chat.id, f"✅ Successfully added {amount} credits to user {user_id}!")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid command format! Use: /addcredits <user_id> <amount>")

# Bot start karega
print("Bot is running...")
bot.polling()