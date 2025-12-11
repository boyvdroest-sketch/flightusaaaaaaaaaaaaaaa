import os
from flask import Flask, request
import telebot
from telebot import types

# Get bot token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Add your admin user ID here
ADMIN_ID = 5408261209  # Replace with your actual Telegram user ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Store user info for replies and broadcast
user_messages = {}
broadcast_users = set()
user_chat_states = {}  # Track user conversation states

# ===== FLIGHT DATA WITH DISCOUNTS =====
FLIGHT_OFFERS = {
    "domestic": {
        "title": "🇺🇸 **Domestic Flights - Up to 50% OFF**",
        "details": """**Top USA Airline Deals:**
• American Airlines: Up to 50% OFF
• Delta Air Lines: 30-45% discounts
• United Airlines: Exclusive member rates
• Southwest: Wanna Get Away fares
• JetBlue: Mint Class savings

**Popular Routes:**
• JFK→LAX: From $189
• ATL→MCO: From $79
• ORD→MIA: From $119
• SFO→SEA: From $129

**Instant Benefits:**
✓ Earn airline miles
✓ Priority boarding options
✓ Free changes on select fares
✓ 24/7 customer support"""
    },
    "crossborder": {
        "title": "🌐 **International Flights - Special Rates**",
        "details": """**Global USA Airline Deals:**
• American Airlines: International routes
• Delta: SkyTeam worldwide network
• United: Star Alliance partners
• Up to 40% off roundtrip

**Top Destinations:**
• Europe: Up to $500 savings
• Asia: 35-45% discounts
• Latin America: Promo fares
• Canada: Cross-border deals"""
    },
    "airtravel": {
        "title": "✈️ **Premium Cabins - Discounted**",
        "details": """**Class Upgrades Available:**
• First Class: Up to 50% OFF
• Business Class: Up to 45% OFF
• Premium Economy: Up to 40% OFF
• Main Cabin: Best value fares

**Airline Benefits:**
• American Flagship First
• Delta One Suites
• United Polaris Business
• Lie-flat seat discounts"""
    },
    "coastal": {
        "title": "🌅 **Coastal Routes - Beach Deals**",
        "details": """**Coastal USA Airline Routes:**
• West Coast: LAX, SFO, SEA, SAN
• East Coast: JFK, MIA, MCO, BOS
• Hawaii: Inter-island specials
• Caribbean: Tropical destinations

**Sample Fares:**
• LAX→SAN: From $89
• JFK→MIA: From $99
• Mainland→HNL: From $299
• Coastal weekend getaways"""
    },
    "flexible": {
        "title": "🔄 **Last Minute - Up to 60% OFF**",
        "details": """**Emergency & Last Minute:**
• 0-3 days: Up to 60% OFF
• 4-7 days: 40-50% discounts
• Same-day departure deals
• Standby special rates

**Flexible Options:**
• Date change flexibility
• Fare lock available
• Low fare calendars
• Close-in booking savings"""
    }
}

@bot.message_handler(commands=['start'])
def start_command(message):
    if message is None:
        return

    # Add user to broadcast list
    user_id = message.from_user.id
    broadcast_users.add(user_id)
    
    # Reset chat state
    user_chat_states[user_id] = 'started'

    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Travel categories
    keyboard.add(types.InlineKeyboardButton("🇺🇸 USA Airlines Deals", callback_data="travel_domestic"))
    keyboard.add(
        types.InlineKeyboardButton("🌐 International", callback_data="travel_crossborder"),
        types.InlineKeyboardButton("✈️ Premium Cabins", callback_data="travel_airtravel")
    )
    keyboard.add(
        types.InlineKeyboardButton("🌅 Coastal Routes", callback_data="travel_coastal"),
        types.InlineKeyboardButton("🔄 Last Minute", callback_data="travel_flexible")
    )
    keyboard.add(types.InlineKeyboardButton("📍 Popular Routes", callback_data="travel_routes"))
    
    # Contact & Channel
    button_channel = types.InlineKeyboardButton("📢 Join Deals", url="https://t.me/flights_bills_b4u")
    button_contact = types.InlineKeyboardButton("💬 Book Now", url="https://t.me/yrfrnd_spidy")
    
    keyboard.add(button_channel, button_contact)

    # MEDIUM LENGTH START MESSAGE
    message_text = (
        "✈️ **Welcome to USA Airline Deals**\n\n"
        
        "**Top Discounts Available:**\n"
        "✅ Up to 50% OFF Domestic Flights\n"
        "✅ Up to 60% OFF Last Minute\n"
        "✅ Premium Cabin Specials\n"
        "✅ Exclusive Member Rates\n\n"
        
        "**Major Airlines:**\n"
        "• American Airlines\n"
        "• Delta Air Lines\n"
        "• United Airlines\n"
        "• Southwest & JetBlue\n\n"
        
        "**How It Works:**\n"
        "1. Select a category below\n"
        "2. View exclusive discounts\n"
        "3. Contact us for booking\n"
        "4. Save on your next flight!\n\n"
        
        "*Limited availability. Contact within 24h for best rates.*"
    )

    bot.send_message(message.chat.id, message_text, reply_markup=keyboard, parse_mode='Markdown')

# ===== TRAVEL HANDLERS =====
@bot.callback_query_handler(func=lambda call: call.data.startswith('travel_'))
def travel_handler(call):
    """Handle travel category clicks"""
    user_id = call.from_user.id
    option = call.data.replace('travel_', '')
    
    if option in FLIGHT_OFFERS:
        offer = FLIGHT_OFFERS[option]
        
        response = f"{offer['title']}\n\n{offer['details']}"
        
        # Action buttons
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📞 Book Now", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Deals Channel", url="https://t.me/flights_bills_b4u")
        )
        markup.add(
            types.InlineKeyboardButton("← Back to Menu", callback_data="travel_more")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "routes":
        response = """📍 **Popular USA Airline Routes**

**American Airlines Deals:**
• JFK→LAX: From $189
• MIA→ORD: From $129
• DFW→LAS: From $99

**Delta Air Lines Specials:**
• ATL→MCO: From $79
• DTW→FLL: From $109
• SLC→DEN: From $89

**United Airlines Offers:**
• EWR→SFO: From $199
• IAH→LAX: From $149
• ORD→MIA: From $119

**Southwest Wanna Get Away:**
• DAL→HOU: From $49
• BWI→TPA: From $69
• MDW→STL: From $59

*All fares one-way. Limited seats available.*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇸 Domestic Deals", callback_data="travel_domestic"),
            types.InlineKeyboardButton("✈️ Premium Cabins", callback_data="travel_airtravel")
        )
        markup.add(
            types.InlineKeyboardButton("📞 Book Route", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("← Back", callback_data="travel_more")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "more":
        # Show all categories
        response = """✈️ **All Travel Categories**

🇺🇸 **Domestic USA Airlines**
• American, Delta, United deals
• Up to 50% discounts
• Popular route specials

🌐 **International Flights**
• Global destinations
• Up to 40% savings
• Alliance partner rates

✈️ **Premium Cabin Upgrades**
• First Class discounts
• Business Class deals
• Extra comfort options

🌅 **Coastal & Beach Routes**
• West & East Coast
• Hawaii & Caribbean
• Vacation packages

🔄 **Last Minute & Flexible**
• Emergency travel
• Same-day deals
• Flexible date options

📍 **Popular Routes**
• Top discounted routes
• Hub-to-hub specials
• Best value fares

*Select a category for details*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇸 Domestic", callback_data="travel_domestic"),
            types.InlineKeyboardButton("🌐 International", callback_data="travel_crossborder")
        )
        markup.add(
            types.InlineKeyboardButton("✈️ Premium", callback_data="travel_airtravel"),
            types.InlineKeyboardButton("🌅 Coastal", callback_data="travel_coastal")
        )
        markup.add(
            types.InlineKeyboardButton("🔄 Last Minute", callback_data="travel_flexible"),
            types.InlineKeyboardButton("📍 Routes", callback_data="travel_routes")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

# ===== BROADCAST FEATURE =====
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "This feature is for administrative use only.")
        return
    
    if len(broadcast_users) == 0:
        bot.reply_to(message, "No users available for notification.")
        return
    
    # Ask admin for broadcast message
    msg = bot.send_message(
        ADMIN_ID,
        f"Send broadcast to {len(broadcast_users)} users:"
    )
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    if hasattr(message, 'is_broadcast_processed') and message.is_broadcast_processed:
        return
    message.is_broadcast_processed = True
    
    broadcast_text = message.text
    users = list(broadcast_users)
    success_count = 0
    fail_count = 0
    
    status_msg = bot.send_message(ADMIN_ID, f"Sending to {len(users)} users...")
    
    for user_id in users:
        try:
            notification = f"✈️ **Flight Deal Alert** ✈️\n\n{broadcast_text}"
            bot.send_message(user_id, notification)
            success_count += 1
        except Exception as e:
            fail_count += 1
    
    bot.edit_message_text(
        f"Broadcast complete!\n\n"
        f"Success: {success_count}\n"
        f"Failed: {fail_count}\n"
        f"Total: {len(users)}",
        ADMIN_ID,
        status_msg.message_id
    )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    user_count = len(broadcast_users)
    bot.send_message(ADMIN_ID, f"Total users: {user_count}")

# ===== CHAT HANDLERS =====
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('hello'))
def hello_handler(message):
    user = message.from_user
    user_id = user.id
    
    broadcast_users.add(user_id)
    user_chat_states[user_id] = 'waiting_for_admin'
    
    user_info = f"User: {user.first_name} {user.last_name or ''} (@{user.username or 'No username'})"
    
    user_messages[message.message_id] = {
        'user_id': user.id,
        'user_info': user_info,
        'original_message': message.text
    }
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📨 Reply", callback_data=f"reply_{message.message_id}"))
    
    forward_text = f"New user greeting\n\n{user_info}\nUser ID: {user.id}\n\n'{message.text}'"
    
    bot.send_message(ADMIN_ID, forward_text, reply_markup=keyboard)
    
    bot.reply_to(message, "Hello! Our team will contact you soon with flight deals.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def reply_callback_handler(call):
    message_id = int(call.data.split('_')[1])
    
    if message_id in user_messages:
        user_data = user_messages[message_id]
        
        msg = bot.send_message(ADMIN_ID, f"Reply to {user_data['user_info']}:")
        bot.register_next_step_handler(msg, process_admin_reply, user_data['user_id'])
    else:
        bot.answer_callback_query(call.id, "Message not found")

def process_admin_reply(message, user_id):
    try:
        bot.send_message(user_id, f"Support reply:\n\n{message.text}")
        bot.reply_to(message, "Reply sent!")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(func=lambda message: True)
def all_messages_handler(message):
    user = message.from_user
    user_id = user.id
    
    if user_id == ADMIN_ID:
        return
    
    broadcast_users.add(user_id)
    
    if user_chat_states.get(user_id) == 'waiting_for_admin' and message.text:
        user_info = f"User: {user.first_name} {user.last_name or ''} (@{user.username or 'No username'})"
        
        user_messages[message.message_id] = {
            'user_id': user_id,
            'user_info': user_info,
            'original_message': message.text
        }
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📨 Reply", callback_data=f"reply_{message.message_id}"))
        
        forward_text = f"User message\n\n{user_info}\nUser ID: {user_id}\n\n'{message.text}'"
        
        bot.send_message(ADMIN_ID, forward_text, reply_markup=keyboard)
        
        if not message.text.lower().startswith('hello'):
            bot.reply_to(message, "Message received. We'll reply soon.")

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flight Deals Bot</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✈️ Flight Deals Bot</h1>
            <p>Get exclusive discounts on USA airline flights</p>
            <p class="status">✅ Bot is Active</p>
            <p>Available airlines: American, Delta, United, Southwest, JetBlue</p>
            <p>Use Telegram bot for real-time deals</p>
        </div>
    </body>
    </html>
    """

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = request.get_data().decode("utf-8")
    update_obj = telebot.types.Update.de_json(update)
    bot.process_new_updates([update_obj])
    return "OK", 200

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Token required")
    
    try:
        bot.remove_webhook()
        replit_domain = os.environ.get("REPLIT_DEV_DOMAIN")
        render_domain = os.environ.get("RENDER_EXTERNAL_URL")
        
        if replit_domain:
            webhook_url = f"https://{replit_domain}/{TOKEN}"
        elif render_domain:
            webhook_url = f"{render_domain}/{TOKEN}"
        else:
            webhook_url = None
            
        if webhook_url:
            bot.set_webhook(url=webhook_url)
            print(f"Bot deployed: {webhook_url}")
        else:
            print("Bot running in polling mode")
            
    except Exception as e:
        print(f"Webhook: {e}")
    
    print("Flight Deals Bot active")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
