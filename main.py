import os
import json
import time
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = "7616068751:AAGKPxZnM2sy4N2mhf8o3HN1QE1AxZw8Yxk"  # Replace with your actual bot token
API_URL = "https://nikhilraghav.site/api/api-proxy.php?numberPlate="
ADMIN_USERNAME = "Piyush8377"  # Admin's username without the '@' symbol
SEARCH_COST = 20  # Points cost for one search
REFERRAL_BONUS = 20  # Points given for referral
DATABASE_FILE = "user_database.json"

# Database structure
if os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "r") as f:
        database = json.load(f)
else:
    database = {
        "users": {},
        "referrals": {}
    }

def save_database():
    """Save the database to a file."""
    with open(DATABASE_FILE, "w") as f:
        json.dump(database, f, indent=4)

def get_user_data(user_id):
    """Get or create user data."""
    user_id = str(user_id)
    if user_id not in database["users"]:
        database["users"][user_id] = {
            "username": "",
            "points": 0,
            "last_free_search": None,
            "unlimited": False
        }
    return database["users"][user_id]

def can_do_free_search(user_id):
    """Check if user can do a free search today."""
    user_data = get_user_data(user_id)
    
    # Admin has unlimited searches
    if user_data.get("unlimited", False):
        return True
    
    today = datetime.now().strftime('%Y-%m-%d')
    last_search = user_data.get("last_free_search")
    
    if last_search is None or last_search != today:
        return True
    return False

def update_free_search(user_id):
    """Update the last free search date."""
    user_data = get_user_data(user_id)
    user_data["last_free_search"] = datetime.now().strftime('%Y-%m-%d')
    save_database()

def deduct_points(user_id):
    """Deduct points for a search."""
    user_id = str(user_id)
    user_data = get_user_data(user_id)
    
    # Don't deduct if user has unlimited access
    if user_data.get("unlimited", False):
        return True
    
    if user_data["points"] >= SEARCH_COST:
        user_data["points"] -= SEARCH_COST
        save_database()
        return True
    return False

def add_referral(referrer_id, referred_id):
    """Add a referral relationship and award points."""
    referrer_id, referred_id = str(referrer_id), str(referred_id)
    
    # Prevent self-referrals
    if referrer_id == referred_id:
        return False
    
    # Check if the referred user is already in the referrals database
    if referred_id in database["referrals"]:
        return False
    
    # Add the referral relationship
    database["referrals"][referred_id] = referrer_id
    
    # Award points to the referrer
    referrer_data = get_user_data(referrer_id)
    referrer_data["points"] += REFERRAL_BONUS
    save_database()
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    user = update.effective_user
    user_id = str(user.id)
    user_data = get_user_data(user_id)
    user_data["username"] = user.username or ""
    save_database()
    
    # Check if user was referred
    if context.args and len(context.args) > 0:
        referrer_id = context.args[0]
        if referrer_id.isdigit():
            if add_referral(referrer_id, user_id):
                await update.message.reply_text(f"You were referred by a user. They received {REFERRAL_BONUS} points!")
    
    # Create the main menu keyboard
    keyboard = [
        [InlineKeyboardButton("🔍 Search Vehicle", callback_data="search")],
        [InlineKeyboardButton("💰 My Points", callback_data="points")],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="refer")],
        [InlineKeyboardButton("📱 Contact Admin", callback_data="contact")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Welcome to Vehicle Info Bot! 🚗\n\n"
        f"This bot helps you fetch vehicle details using registration numbers.\n\n"
        f"• You get 1 free search daily\n"
        f"• Each additional search costs {SEARCH_COST} points\n"
        f"• Refer friends to earn {REFERRAL_BONUS} points per referral\n\n"
        f"Use the menu below to navigate:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔍 *Vehicle Info Bot Help*\n\n"
        "*How to use:*\n"
        "• Send a vehicle registration number to get details\n"
        "• You get 1 free search per day\n"
        "• Additional searches cost points\n\n"
        "*Commands:*\n"
        "• /start - Start the bot and see main menu\n"
        "• /help - Show this help message\n"
        "• /points - Check your points balance\n"
        "• /refer - Get your referral link\n\n"
        "*Earning Points:*\n"
        f"• Each referral gives you {REFERRAL_BONUS} points\n"
        f"• Each search costs {SEARCH_COST} points\n\n"
        "*For Unlimited Access:*\n"
        f"• Contact @{ADMIN_USERNAME} to purchase unlimited access",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def points_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /points command."""
    user_id = str(update.effective_user.id)
    user_data = get_user_data(user_id)
    
    keyboard = [
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="refer")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status = "Standard Account"
    if user_data.get("unlimited", False):
        status = "Unlimited Access ✓"
    
    await update.message.reply_text(
        f"💰 *Your Points Balance*\n\n"
        f"Points: *{user_data['points']}*\n"
        f"Status: *{status}*\n\n"
        f"• 1 free search per day\n"
        f"• Each additional search costs {SEARCH_COST} points\n"
        f"• Refer friends to earn more points!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def refer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /refer command."""
    user_id = str(update.effective_user.id)
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👥 *Refer & Earn Points*\n\n"
        f"Share your referral link with friends. When they join using your link, "
        f"you'll receive *{REFERRAL_BONUS} points* per referral!\n\n"
        f"*Your Referral Link:*\n`{referral_link}`\n\n"
        f"Share this link with your friends to earn points!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def add_points_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to add points to user."""
    user_id = str(update.effective_user.id)
    user_data = get_user_data(user_id)
    
    # Check if user is admin
    if user_data.get("username", "") != ADMIN_USERNAME:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    # Check arguments
    if not context.args or len(context.args) != 2:
        await update.message.reply_text(
            "⚠️ Usage: /addpoints <user_id> <points>\n\n"
            "Example: /addpoints 123456789 100"
        )
        return
    
    try:
        target_user_id = str(context.args[0])
        points_to_add = int(context.args[1])
        
        if points_to_add <= 0:
            await update.message.reply_text("⚠️ Points must be a positive number.")
            return
        
        target_user_data = get_user_data(target_user_id)
        target_user_data["points"] += points_to_add
        save_database()
        
        await update.message.reply_text(
            f"✅ Successfully added {points_to_add} points to user {target_user_id}.\n"
            f"Their new balance is {target_user_data['points']} points."
        )
    except ValueError:
        await update.message.reply_text("⚠️ Invalid input. Points must be a number.")

async def set_unlimited_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to set a user to unlimited status."""
    user_id = str(update.effective_user.id)
    user_data = get_user_data(user_id)
    
    # Check if user is admin
    if user_data.get("username", "") != ADMIN_USERNAME:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    # Check arguments
    if not context.args or len(context.args) != 2:
        await update.message.reply_text(
            "⚠️ Usage: /setunlimited <user_id> <true/false>\n\n"
            "Example: /setunlimited 123456789 true"
        )
        return
    
    try:
        target_user_id = str(context.args[0])
        unlimited_status = context.args[1].lower() == "true"
        
        target_user_data = get_user_data(target_user_id)
        target_user_data["unlimited"] = unlimited_status
        save_database()
        
        status_text = "unlimited access" if unlimited_status else "standard access"
        await update.message.reply_text(
            f"✅ Successfully set user {target_user_id} to {status_text}."
        )
    except:
        await update.message.reply_text("⚠️ An error occurred while processing your request.")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    
    if query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🔍 Search Vehicle", callback_data="search")],
            [InlineKeyboardButton("💰 My Points", callback_data="points")],
            [InlineKeyboardButton("👥 Refer & Earn", callback_data="refer")],
            [InlineKeyboardButton("📱 Contact Admin", callback_data="contact")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="Vehicle Info Bot 🚗\n\nUse the menu below to navigate:",
            reply_markup=reply_markup
        )
    
    elif query.data == "search":
        await query.edit_message_text(
            text="🔍 *Vehicle Search*\n\n"
                 "Please enter a vehicle registration number to get details.\n\n"
                 "Example formats: DL01AB1234, MH02CD5678",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]])
        )
        context.user_data["awaiting_reg_number"] = True
    
    elif query.data == "points":
        user_data = get_user_data(user_id)
        
        keyboard = [
            [InlineKeyboardButton("👥 Refer & Earn", callback_data="refer")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status = "Standard Account"
        if user_data.get("unlimited", False):
            status = "Unlimited Access ✓"
        
        await query.edit_message_text(
            text=f"💰 *Your Points Balance*\n\n"
                 f"Points: *{user_data['points']}*\n"
                 f"Status: *{status}*\n\n"
                 f"• 1 free search per day\n"
                 f"• Each additional search costs {SEARCH_COST} points\n"
                 f"• Refer friends to earn more points!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif query.data == "refer":
        referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"👥 *Refer & Earn Points*\n\n"
                 f"Share your referral link with friends. When they join using your link, "
                 f"you'll receive *{REFERRAL_BONUS} points* per referral!\n\n"
                 f"*Your Referral Link:*\n`{referral_link}`\n\n"
                 f"Share this link with your friends to earn points!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif query.data == "contact":
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"📱 *Contact Admin*\n\n"
                 f"Need unlimited access or have questions?\n"
                 f"Contact @{ADMIN_USERNAME} directly.\n\n"
                 f"Unlimited access gives you:\n"
                 f"• Unlimited vehicle searches\n"
                 f"• No daily limits\n"
                 f"• Priority support",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif query.data == "help":
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="🔍 *Vehicle Info Bot Help*\n\n"
                 "*How to use:*\n"
                 "• Send a vehicle registration number to get details\n"
                 "• You get 1 free search per day\n"
                 "• Additional searches cost points\n\n"
                 "*Commands:*\n"
                 "• /start - Start the bot and see main menu\n"
                 "• /help - Show this help message\n"
                 "• /points - Check your points balance\n"
                 "• /refer - Get your referral link\n\n"
                 "*Earning Points:*\n"
                 f"• Each referral gives you {REFERRAL_BONUS} points\n"
                 f"• Each search costs {SEARCH_COST} points\n\n"
                 "*For Unlimited Access:*\n"
                 f"• Contact @{ADMIN_USERNAME} to purchase unlimited access",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages (vehicle registration numbers)."""
    # Check if we're expecting a registration number
    if not context.user_data.get("awaiting_reg_number", False):
        keyboard = [
            [InlineKeyboardButton("🔍 Search Vehicle", callback_data="search")],
            [InlineKeyboardButton("💰 My Points", callback_data="points")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Please use the menu below or type /start to navigate:",
            reply_markup=reply_markup
        )
        return
    
    # Reset awaiting flag
    context.user_data["awaiting_reg_number"] = False
    
    # Get the registration number from the message
    reg_number = update.message.text.strip().upper()
    
    # Validate registration number format (basic validation)
    if not reg_number or len(reg_number) < 4:
        await update.message.reply_text(
            "⚠️ Invalid registration number format.\n\n"
            "Please try again with a valid format (e.g., DL01AB1234).",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔍 Try Again", callback_data="search")
            ]])
        )
        return
    
    # Get user data
    user_id = str(update.effective_user.id)
    user_data = get_user_data(user_id)
    
    # Check if the user can make a free search or has enough points
    if can_do_free_search(user_id):
        update_free_search(user_id)
        search_type = "Free Daily Search"
    elif deduct_points(user_id):
        search_type = f"Paid Search (-{SEARCH_COST} points)"
    else:
        # Not enough points
        keyboard = [
            [InlineKeyboardButton("👥 Refer to Earn Points", callback_data="refer")],
            [InlineKeyboardButton("📱 Contact Admin for Unlimited", callback_data="contact")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ *Not enough points*\n\n"
            f"You've used your free daily search and don't have enough points "
            f"for additional searches.\n\n"
            f"Current points: *{user_data['points']}*\n"
            f"Required points: *{SEARCH_COST}*\n\n"
            f"Refer friends to earn more points or contact admin for unlimited access.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, 
        action="typing"
    )
    
    # Make API request
    try:
        await update.message.reply_text("🔍 Searching for vehicle details...")
        
        response = requests.get(f"{API_URL}{reg_number}", timeout=30)
        
        if response.status_code != 200:
            await update.message.reply_text(
                f"⚠️ Error: API returned status code {response.status_code}.\n\n"
                f"Please try again later or contact @{ADMIN_USERNAME} for support.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                ]])
            )
            return
        
        data = response.json()
        
        # Check if the API returned an error
        if data.get("statusCode") != 200 or "response" not in data:
            await update.message.reply_text(
                f"⚠️ Error: Could not find vehicle information.\n\n"
                f"Message: {data.get('message', 'Unknown error')}\n\n"
                f"Please check the registration number and try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔍 Try Again", callback_data="search"),
                    InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
                ]])
            )
            return
        
        # Extract vehicle information
        vehicle_info = data.get("response", {})
        
        # Format the response
        info_text = (
            f"🚗 *Vehicle Information*\n\n"
                f"🔹 *Registration Details*\n"
                f"*➤ Registration Number:* {vehicle_info.get('regNo', 'N/A')}\n"
                f"*➤ RTO Code:* {vehicle_info.get('rtoCode', 'N/A')}\n"
                f"*➤ Registration Authority:* {vehicle_info.get('regAuthority', 'N/A')}\n"
                f"*➤ Registration Date:* {vehicle_info.get('regDate', 'N/A')}\n\n"

                f"🔹 *Vehicle Specifications*\n"
                f"*➤ Vehicle Class:* {vehicle_info.get('vehicleClass', 'N/A')}\n"
                f"*➤ Manufacturer:* {vehicle_info.get('manufacturer', 'N/A')}\n"
                f"*➤ Model:* {vehicle_info.get('vehicle', 'N/A')} ({vehicle_info.get('variant', 'N/A')})\n"
                f"*➤ Fuel Type:* {vehicle_info.get('fuelType', 'N/A')}\n"
                f"*➤ Cubic Capacity:* {vehicle_info.get('cubicCapacity', 'N/A')} cc\n"
                f"*➤ Vehicle Type:* {vehicle_info.get('vehicleType', 'N/A')}\n"
                f"*➤ Seat Capacity:* {vehicle_info.get('seatCapacity', 'N/A')}\n"
                f"*➤ Commercial Vehicle:* {'Yes' if vehicle_info.get('isCommercial') else 'No'}\n\n"

                f"🔹 *Owner Information*\n"
                f"*➤ Owner Name:* {vehicle_info.get('owner', 'N/A')}\n"
                f"*➤ Father's Name:* {vehicle_info.get('ownerFatherName', 'N/A')}\n"
                f"*➤ Permanent Address:* {vehicle_info.get('permAddress', 'N/A')}\n"
                f"*➤ Pincode:* {vehicle_info.get('pincode', 'N/A')}\n\n"

                f"🔹 *Financial & Insurance Details*\n"
                f"*➤ Financer Name:* {vehicle_info.get('financerName', 'N/A')}\n"
                f"*➤ Insurance Company:* {vehicle_info.get('insuranceCompanyName', 'N/A')}\n"
                f"*➤ Insurance Validity:* {vehicle_info.get('insuranceUpto', 'N/A')}\n"
                f"*➤ Insurance Expired:* {'Yes' if vehicle_info.get('insuranceExpired') else 'No'}\n\n"

                f"🔹 *PUC Details*\n"
                f"*➤ PUCC Number:* {vehicle_info.get('puccNumber', 'N/A')}\n"
                f"*➤ PUCC Validity:* {vehicle_info.get('puccValidUpto', 'N/A')}\n\n"

                f"🔹 *Additional Information*\n"
                f"*➤ Chassis Number:* {vehicle_info.get('chassis', 'N/A')}\n"
                f"*➤ Engine Number:* {vehicle_info.get('engine', 'N/A')}\n"
                f"*➤ Data Status:* {vehicle_info.get('dataStatus', 'N/A')}\n"
                f"*➤ Last Updated:* {vehicle_info.get('lmDate', 'N/A')}\n\n"
                
                f"*⭒ Powered By: @VEHICLEINFOIND_BOT*\n\n"
            
            f"Search Type: *{search_type}*\n"
            f"Points Remaining: *{user_data['points']}*"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔍 New Search", callback_data="search")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            info_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        # Log the error
        logger.error(f"Error fetching vehicle data: {str(e)}")
        
        await update.message.reply_text(
            f"⚠️ An error occurred while fetching vehicle information.\n\n"
            f"Error: {str(e)}\n\n"
            f"Please try again later or contact @{ADMIN_USERNAME} for support.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
            ]])
        )

async def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("points", points_command))
    application.add_handler(CommandHandler("refer", refer_command))
    application.add_handler(CommandHandler("addpoints", add_points_command))
    application.add_handler(CommandHandler("setunlimited", set_unlimited_command))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()  # ✅ Async function ke andar

if __name__ == "__main__":
    asyncio.run(main())  # ✅ Async execution
