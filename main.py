import telebot
import requests
import re

# Replace with your bot token and group ID
BOT_TOKEN = "7738466078:AAE2CczVGjy0HZwQVgnKXUx-BI-CN0D-cQ8"
GROUP_ID = -1002320210604  # Replace with your actual group ID

bot = telebot.TeleBot(BOT_TOKEN)

def fetch_vehicle_details(plate_number):
    url = f"https://car.app/api/vehicle?numberPlate={plate_number}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get("response")
        if data:  
            return format_vehicle_details(data)
    
    return None  

def format_vehicle_details(data):
    financed_status = "Yes" if data.get("financerName") and data["financerName"].lower() != "on cash" else "No"
    rc_status = data.get("status", "N/A")

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

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == "private":
        bot.reply_to(message, "❌ This bot works only in @RtoVehicle group.")
    else:
        bot.reply_to(message, "Send a vehicle number to get details.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.id != GROUP_ID:
        return  

    plate_number = message.text.strip().upper()

    # Check if the vehicle number is valid (max 10 characters, no spaces)
    if not re.match(r"^[A-Z0-9]{1,10}$", plate_number):
        return  # Ignore invalid numbers (no response)

    details = fetch_vehicle_details(plate_number)
    
    if details:
        bot.reply_to(message, details)
    else:
        bot.reply_to(message, "❌ No details found for this vehicle number.")

bot.polling()
