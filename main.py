import telebot
import requests

# Bot Token
BOT_TOKEN = "7738466078:AAE2CczVGjy0HZwQVgnKXUx-BI-CN0D-cQ8"
bot = telebot.TeleBot(BOT_TOKEN)

# Allowed Group ID
ALLOWED_GROUP_ID = -1002320210604  # @RtoVehicle group ID

# Bot Owner ID
BOT_OWNER_ID = 7394317325

# Users ke credits store karne ke liye
user_credits = {}

# Active searches dictionary
active_searches = {}

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

    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Store user_id in active searches
    active_searches[user_id] = True  

    bot.send_message(message.chat.id, f"🔍 {user_name}, Enter vehicle number (e.g., GJ01KD1255):")  

# Fetch Vehicle Info
@bot.message_handler(func=lambda message: message.from_user.id in active_searches)
def fetch_vehicle_info(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if message.chat.id != ALLOWED_GROUP_ID:
        return  

    if not message.text:  
        bot.send_message(message.chat.id, "❌ Please send a valid vehicle number!")  
        return  

    if user_id not in user_credits:  
        user_credits[user_id] = 60    

    if user_credits[user_id] < 20:  
        keyboard = telebot.types.InlineKeyboardMarkup()  
        buy_button = telebot.types.InlineKeyboardButton("💳 Buy Credit", url="https://t.me/bjxxjjhbb")  
        keyboard.add(buy_button)  
        bot.send_message(message.chat.id, "❌ You have run out of credits!", reply_markup=keyboard)  
        return  

    reg_no = message.text.strip().upper()  
    bot.send_message(message.chat.id, f"🔍 {user_name}, Fetching details, please wait...")  

    details = get_vehicle_details(reg_no)  

    user_credits[user_id] -= 20  # Deduct 20 credits per search  
    bot.send_message(message.chat.id, details, reply_markup=main_menu())

    # Remove user from active searches after successful search
    del active_searches[user_id]

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

        if user_id not in user_credits:
            user_credits[user_id] = 60  # Default credits if user is new

        user_credits[user_id] += amount

        bot.reply_to(message, f"✅ Added {amount} credits to user {user_id}.\nTotal Credits: {user_credits[user_id]}")
    
    except ValueError:
        bot.reply_to(message, "❌ Invalid format! Use `/addcredits <user_id> <amount>`", parse_mode="Markdown")

# Start Bot
print("Bot is running...")
bot.polling(non_stop=True, timeout=90, long_polling_timeout=90)
