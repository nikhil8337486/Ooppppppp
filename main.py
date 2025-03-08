import os
import json
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Bot Token and Channel
TOKEN = "7738466078:AAH2qHH0PZBLFompWoQBdf7jtpn2XTvRnJI"
API_URL = "https://carflow-mocha.vercel.app/api/vehicle?numberPlate={}"
CHANNEL = "@RtoVehicle"

# Admin List (Replace with actual Telegram user IDs)
ADMIN_IDS = [7394317325]

# User data file
USER_DATA_FILE = "users.json"

# Load user data from file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save user data to file
def save_users():
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Load users initially
users = load_users()

# Check if user has joined the channel
def is_subscribed(user_id, context):
    try:
        chat_member = context.bot.get_chat_member(CHANNEL, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

# Start command
def start(update: Update, context: CallbackContext):
    user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = str(user.id)  # Convert to string

    if user_id not in users:
        users[user_id] = {"balance": 10, "referrals": 0}
        save_users()  # Save user data

        # Handle Referral System
        if context.args:  # If user joined via referral link
            referrer_id = str(context.args[0])
            if referrer_id in users and referrer_id != user_id:
                users[referrer_id]["balance"] += 20  # Add 20 points to referrer
                users[referrer_id]["referrals"] += 1  # Increment referral count
                save_users()

    if not is_subscribed(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ Joined", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            update.message.reply_text(
                "😎 Hey! To use this bot, please join our channel first and click '✅ Joined'.",
                reply_markup=reply_markup
            )
        elif update.callback_query:
            update.callback_query.message.reply_text(
                "😎 Hey! To use this bot, please join our channel first and click '✅ Joined'.",
                reply_markup=reply_markup
            )
        return

    keyboard = [
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("🎉 Referral", callback_data="refer")],
        [InlineKeyboardButton("🔍 Search Details", callback_data="search")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        f"🌟 Welcome, {user.first_name}! 🌟\n\n"
        "🚀 Your gateway to instant and accurate vehicle information.\n\n"
        "🔧 *What this bot offers:*\n"
        "🚗 Quick vehicle detail searches.\n"
        "💰 Secure deposit options for premium services.\n"
        "👥 Earn rewards by inviting friends.\n"
        "📊 Track global bot statistics and user engagement.\n\n"
        "⚡ Start exploring now and experience seamless service! 🚀"
    )

    if update.message:
        update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        update.callback_query.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

# Check Subscription
def check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)  # Convert to string

    if is_subscribed(user_id, context):
        query.message.delete()
        start(update, context)  # Call start to continue bot usage
    else:
        query.answer("❌ Please join the channel first!", show_alert=True)

# Profile Section
def profile(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)  # Convert to string
    user = users.get(user_id, {"balance": 0, "referrals": 0})

    query.message.reply_text(
        f"🆔 User ID: {user_id}\n💰 Balance: {user['balance']} Points\n🎯 Total Referrals: {user['referrals']}"
    )

# Referral System
def refer(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)  # Convert to string
    referral_link = f"https://t.me/VEHICLEINFOIND_BOT?start={user_id}"

    query.message.reply_text(
        f"🔥 Refer and earn 20 points!\n🔗 Your Referral Link: {referral_link}"
    )

# Search Vehicle Details
def search(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)  # Convert to string

    if users[user_id]["balance"] < 10:
        query.message.reply_text("❌ You don't have enough points. Please deposit first.")
        return

    query.message.reply_text("🔍 Please enter the vehicle number:")
    context.user_data[user_id] = {"awaiting_input": True}

# Handle user input
def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.message.chat_id)  # Convert to string
    text = update.message.text

    if context.user_data.get(user_id, {}).get("awaiting_input"):
        del context.user_data[user_id]["awaiting_input"]
        users[user_id]["balance"] -= 10
        save_users()  # Save updated balance

        try:
            response = requests.get(API_URL.format(text))
            data = response.json()

            if data.get("statusCode") == 200:
                vehicle_info = data["response"]

                message = f"""━━━━━━━━━━━━━━━━━━━━━━  
🚗 *Vehicle Information*  
━━━━━━━━━━━━━━━━━━━━━━  

🔹 *Registration Details*  
Registration Number: {vehicle_info.get("regNo", "N/A")}  
RTO Code: {vehicle_info.get("rtoCode", "N/A")}  
Registration Authority: {vehicle_info.get("regAuthority", "N/A")}  
Registration Date: {vehicle_info.get("regDate", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  

🔹 *Vehicle Specifications*  
Vehicle Class: {vehicle_info.get("vehicleClass", "N/A")}  
Manufacturer: {vehicle_info.get("manufacturer", "N/A")}  
Model: {vehicle_info.get("vehicle", "N/A")} ({vehicle_info.get("variant", "N/A")})  
Fuel Type: {vehicle_info.get("fuelType", "N/A")}  
Cubic Capacity: {vehicle_info.get("cubicCapacity", "N/A")} cc  
Vehicle Type: {vehicle_info.get("vehicleType", "N/A")}  
Seat Capacity: {vehicle_info.get("seatCapacity", "N/A")}  
Commercial Vehicle: {"Yes" if vehicle_info.get("isCommercial") else "No"}  

━━━━━━━━━━━━━━━━━━━━━━  

🔹 *Owner Information*  
Owner Name: {vehicle_info.get("owner", "N/A")}  
Father's Name: {vehicle_info.get("ownerFatherName", "N/A")}  
Permanent Address: {vehicle_info.get("permAddress", "N/A")}  
Pincode: {vehicle_info.get("pincode", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  

🔹 *Financial & Insurance Details*  
Financer Name: {vehicle_info.get("financerName", "N/A")}  
Insurance Company: {vehicle_info.get("insuranceCompanyName", "N/A")}  
Insurance Policy Number: {vehicle_info.get("insurancePolicyNumber", "N/A")}  
Insurance Validity: {vehicle_info.get("insuranceUpto", "N/A")}  
Insurance Expired: {"Yes" if vehicle_info.get("insuranceExpired") else "No"}  

━━━━━━━━━━━━━━━━━━━━━━  

🔹 *PUC Details*  
PUCC Number: {vehicle_info.get("puccNumber", "N/A")}  
PUCC Validity: {vehicle_info.get("puccValidUpto", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  

🔹 *Additional Information*  
Chassis Number: {vehicle_info.get("chassis", "N/A")}  
Engine Number: {vehicle_info.get("engine", "N/A")}  
Vehicle Age: {vehicle_info.get("vehicleAge", "N/A")}  
Data Status: {vehicle_info.get("dataStatus", "N/A")}  
Last Updated: {vehicle_info.get("lmDate", "N/A")}  

━━━━━━━━━━━━━━━━━━━━━━  
⭒ *Powered By:* @VEHICLEINFOIND_BOT  
━━━━━━━━━━━━━━━━━━━━━━"""

                update.message.reply_text(message, parse_mode="Markdown")
            else:
                update.message.reply_text("❌ Vehicle data not found, please enter a valid number.")

        except Exception as e:
            logging.error(f"API Error: {e}")
            update.message.reply_text("⚠️ Error fetching data from API. Please try again later.")

# Fixed `/addcredits` command
def add_credits(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    try:
        args = context.args
        if len(args) != 2:
            update.message.reply_text("⚠️ Usage: /addcredits <user_id> <amount>")
            return

        user_id = str(args[0])
        amount = int(args[1])

        if user_id not in users:
            update.message.reply_text(f"❌ User {user_id} not found.")
            return

        users[user_id]["balance"] += amount
        save_users()
        update.message.reply_text(f"✅ Successfully added {amount} points to user {user_id}.")

    except ValueError:
        update.message.reply_text("⚠️ Invalid input. Use: /addcredits <user_id> <amount>")

# Main Function
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("addcredits", add_credits))  
    dp.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_subscription$"))
    dp.add_handler(CallbackQueryHandler(profile, pattern="^profile$"))
    dp.add_handler(CallbackQueryHandler(refer, pattern="^refer$"))
    dp.add_handler(CallbackQueryHandler(search, pattern="^search$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
