import os
from flask import Flask, request
import telebot
from telebot import types

# Get bot token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Add your admin user ID here
ADMIN_ID = 7016264130  # Replace with your actual Telegram user ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Store user info for replies and broadcast
user_messages = {}
broadcast_users = set()
user_chat_states = {}  # Track user conversation states

# ===== COPYRIGHT-SAFE FLIGHT DATA =====
FLIGHT_OFFERS = {
    "domestic": {
        "title": "🇺🇸 **Domestic Air Travel - Significant Savings Available**",
        "details": """**Domestic Flight Opportunities** - Find substantial savings on air travel within the country across various regions and routes.

🚀 **Popular Domestic Routes:**
• **East Coast to Florida**: Competitive pricing available
• **West Coast to Entertainment Destinations**: Value offers
• **Midwest to Vacation Spots**: Attractive rate options
• **Southwest to Mountain Regions**: Cost-effective travel
• **Pacific Northwest to California**: Budget-friendly fares

✈️ **Air Travel Providers:**
• Major full-service carriers
• Value-focused airlines
• Regional flight operators
• Premium service providers
• Budget-friendly options

📍 **Major Travel Hubs:**
Multiple departure points nationwide

📋 **Travel Features:**
✅ Flexible travel dates
✅ Various cabin options
✅ Multiple departure times
✅ Different service levels

🔍 **Travel Planning:** Domestic flights, air travel deals, regional routes, affordable airfare"""
    },
    "crossborder": {
        "title": "🌐 **Cross-Border Travel - International Options**",
        "details": """**International Travel Opportunities** - Explore travel options between countries with various savings opportunities.

🚀 **Cross-Border Routes:**
• **Major US Cities to Canadian Destinations**: Competitive international rates
• **Pacific Coast to Neighbor Country**: Value international travel
• **Northern States to Border Cities**: Attractive cross-border fares
• **Coastal Cities to International Hubs**: Diverse route options
• **Business Centers to International Destinations**: Global travel solutions

✈️ **International Providers:**
• Cross-border service carriers
• International route operators
• Global airline networks
• Regional international services
• Multi-country flight options

📍 **International Gateways:**
Major airports with international service

📋 **Cross-Border Features:**
✅ International travel options
✅ Multiple currency payments
✅ Customs information available
✅ Global destination access

🔍 **Travel Planning:** International flights, cross-border travel, global destinations, overseas travel"""
    },
    "airtravel": {
        "title": "✈️ **Air Travel Options - Various Service Levels**",
        "details": """**Flight Service Categories** - Different levels of air travel service available with varying features and pricing.

✈️ **AIR TRAVEL CATEGORIES:**

**FULL-SERVICE OPTIONS:**
Comprehensive travel experience with additional amenities and services

**PREMIUM SERVICE LEVELS:**
Enhanced travel comfort with extra space and service features

**STANDARD ECONOMY SERVICES:**
Basic air travel with essential amenities at competitive rates

**VALUE-FOCUSED OPTIONS:**
Budget-conscious travel solutions with flexible features

**REGIONAL SERVICE PROVIDERS:**
Local and regional route specialists with focused destination networks

📋 **TRAVEL SERVICE FEATURES:**
✅ Multiple service level choices
✅ Various baggage options
✅ Different seating arrangements
✅ Meal service variations
✅ Entertainment options

💡 **Travel Tip:** Compare different service levels for best value"""
    },
    "coastal": {
        "title": "🌅 **Coastal Route Travel - Coastal Destination Options**",
        "details": """**Coastal Travel Routes** - Access to coastal destinations with various travel options and scheduling flexibility.

🚀 **WESTERN COASTAL ROUTES:**
• **California Coast Cities**: Multiple coastal destination options
• **Pacific Northwest Coastal**: Scenic route availability
• **Desert to Coast Routes**: Diverse landscape travel
• **Mountain to Ocean Travel**: Varied geography options
• **Island Destination Access**: Coastal island routes

🚀 **EASTERN COASTAL ROUTES:**
• **Atlantic Coast Cities**: Eastern seaboard destinations
• **Southern Coastal Routes**: Warm weather destinations
• **Northeast Coastal Travel**: Historical coastal cities
• **Florida Coastal Access**: Multiple coastal points
• **Gulf Coast Destinations**: Southern coastal options

📍 **COASTAL ACCESS POINTS:**
Multiple coastal region airports

📋 **COASTAL TRAVEL FEATURES:**
✅ Beach destination access
✅ Coastal city connections
✅ Seasonal coastal travel
✅ Waterfront destination options

🔍 **Travel Planning:** Coastal flights, beach destinations, oceanfront travel, seaside routes"""
    },
    "flexible": {
        "title": "🔄 **Flexible Travel Options - Various Booking Windows**",
        "details": """**Flexible Travel Planning** - Different booking timeframes and travel flexibility options available.

⏰ **TRAVEL BOOKING CATEGORIES:**

**SHORT-NOTICE TRAVEL:**
Travel options available with minimal advance planning

**ADVANCE BOOKING OPTIONS:**
Planned travel with extended booking windows

**WEEKEND TRAVEL PACKAGES:**
Friday to Sunday travel arrangements

**SPECIAL CIRCUMSTANCE TRAVEL:**
Travel solutions for specific needs and situations

**SEASONAL TRAVEL OPTIONS:**
Time-specific travel opportunities

🕒 **BOOKING WINDOWS:**
• Short-notice: Various options
• 1-3 days: Multiple choices
• Weekend: Special arrangements
• Specific needs: Tailored solutions

📋 **FLEXIBILITY FEATURES:**
✅ Multiple date options
✅ Various departure times
✅ Different return choices
✅ Change option availability

🔍 **Travel Planning:** Last minute travel, flexible booking, short notice flights, spontaneous travel"""
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
    
    # Generic travel categories (copyright-safe)
    keyboard.add(types.InlineKeyboardButton("🇺🇸 Domestic Travel", callback_data="travel_domestic"))
    keyboard.add(
        types.InlineKeyboardButton("🌐 Cross-Border", callback_data="travel_crossborder"),
        types.InlineKeyboardButton("✈️ Service Options", callback_data="travel_airtravel")
    )
    keyboard.add(
        types.InlineKeyboardButton("🌅 Coastal Routes", callback_data="travel_coastal"),
        types.InlineKeyboardButton("🔄 Flexible Travel", callback_data="travel_flexible")
    )
    keyboard.add(types.InlineKeyboardButton("📍 Popular Routes", callback_data="travel_routes"))
    keyboard.add(types.InlineKeyboardButton("📋 Travel Features", callback_data="travel_features"))
    
    # Contact & Channel
    button_channel = types.InlineKeyboardButton("📢 Join Travel Updates", url="https://t.me/flights_bills_b4u")
    button_contact1 = types.InlineKeyboardButton("💬 Contact Support", url="https://t.me/yrfrnd_spidy")
    button_contact2 = types.InlineKeyboardButton("📞 Alternative Contact", url="https://t.me/Eatsplugsus")
    
    keyboard.add(button_channel)
    keyboard.add(button_contact1, button_contact2)

    # ENHANCED FIRST MESSAGE WITH STRONG IMPACT
    message_text = (
        "✈️ **Discover Smart Travel Values** ✈️\n\n"
        
        "🌟 **EXCLUSIVE PLANNING BENEFITS** 🌟\n"
        "Users working with our planning service regularly discover:\n"
        "• **50%+ potential savings** on select travel components\n"
        "• **Hidden value opportunities** not visible in standard searches\n"
        "• **Time-optimized strategies** for busy schedules\n"
        "• **Personalized approaches** tailored to your needs\n\n"
        
        "🚀 **HOW TO ACCESS THESE BENEFITS:**\n"
        "1. Share your travel interests using categories below\n"
        "2. Receive customized planning insights and strategies\n"
        "3. Connect with specialists for detailed implementation\n"
        "4. Implement discovered savings opportunities\n\n"
        
        "💡 *Important: Actual savings vary based on travel dates, availability, and provider policies. "
        "This service provides planning assistance and general travel information. "
        "We are not affiliated with specific airlines, hotels, or travel providers.*\n\n"
        
        "👇 **START YOUR VALUE DISCOVERY NOW:**"
    )

    bot.send_message(message.chat.id, message_text, reply_markup=keyboard, parse_mode='Markdown')

# ===== COPYRIGHT-SAFE TRAVEL HANDLERS =====
@bot.callback_query_handler(func=lambda call: call.data.startswith('travel_'))
def travel_handler(call):
    """Handle travel category clicks - show generic travel information"""
    user_id = call.from_user.id
    option = call.data.replace('travel_', '')
    
    if option in FLIGHT_OFFERS:
        offer = FLIGHT_OFFERS[option]
        
        # Detailed response with disclaimer
        disclaimer = "*Note: This is travel planning information. Specific providers and rates subject to availability.*\n\n"
        response = f"{offer['title']}\n\n{disclaimer}{offer['details']}"
        
        # Action buttons
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📢 Join for Updates", url="https://t.me/flights_bills_b4u"),
            types.InlineKeyboardButton("💬 Contact Support", url="https://t.me/yrfrnd_spidy")
        )
        markup.add(
            types.InlineKeyboardButton("📞 Alternative Contact", url="https://t.me/Eatsplugsus"),
            types.InlineKeyboardButton("✈️ More Options", callback_data="travel_more")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "routes":
        response = """📍 **Common Travel Routes - Planning Information**

🚀 **FREQUENTLY TRAVELED ROUTES:**

**EASTERN REGION ROUTES:**
• Major Northeast cities to Florida destinations
• Mid-Atlantic cities to Southern locations
• New England to Midwestern destinations
• Atlantic Coast to Central regions
• Northeastern hubs to various destinations

**WESTERN REGION ROUTES:**
• Pacific Coast cities to desert destinations
• Northwestern cities to California locations
• Mountain region to coastal destinations
• Southwestern cities to various regions
• Western hubs to multiple destinations

**CROSS-COUNTRY ROUTES:**
• Eastern cities to Western destinations
• Coastal cities to opposite coast
• Northern cities to Southern locations
• Major hubs to various regions
• Regional centers to different areas

**INTERNATIONAL ACCESS:**
• Major US cities to international destinations
• Border states to neighbor country cities
• Coastal cities to overseas locations
• Business centers to global destinations

💡 **Travel Planning Tip:** Consider multiple departure airports and alternative dates for best options."""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇸 Domestic Travel", callback_data="travel_domestic"),
            types.InlineKeyboardButton("✈️ Service Options", callback_data="travel_airtravel")
        )
        markup.add(
            types.InlineKeyboardButton("📢 Join Updates", url="https://t.me/flights_bills_b4u"),
            types.InlineKeyboardButton("📞 Alt Contact", url="https://t.me/Eatsplugsus")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "features":
        response = """📋 **Travel Service Features - General Information**

**TRAVEL SERVICE CATEGORIES:**

**SERVICE LEVEL VARIATIONS:**
Different levels of service available with varying amenities and features

**BAGGAGE OPTIONS:**
Various baggage allowance and handling options

**SEATING ARRANGEMENTS:**
Different seating configurations and comfort levels

**MEAL SERVICE VARIATIONS:**
Various food and beverage service options

**ENTERTAINMENT CHOICES:**
Different in-flight entertainment systems and content

**BOOKING FLEXIBILITY:**
Various change and cancellation policy options

**CHECK-IN OPTIONS:**
Multiple check-in method availability

**LOUNGE ACCESS:**
Various airport lounge access options

**PRIORITY SERVICES:**
Different priority handling options available

**SPECIAL ASSISTANCE:**
Various special needs assistance services

💎 **General Travel Tips:**
1. Review all service terms before booking
2. Compare different service providers
3. Check multiple booking platforms
4. Consider travel insurance options
5. Verify all travel documentation requirements

*This information is for general travel planning purposes.*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✈️ Service Options", callback_data="travel_airtravel"),
            types.InlineKeyboardButton("🔄 Flexible Travel", callback_data="travel_flexible")
        )
        markup.add(
            types.InlineKeyboardButton("📢 Join for Updates", url="https://t.me/flights_bills_b4u"),
            types.InlineKeyboardButton("💬 Contact Support", url="https://t.me/yrfrnd_spidy")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "more":
        # Show all categories
        response = """✈️ **Travel Planning Categories**

🇺🇸 **DOMESTIC TRAVEL OPTIONS:**
• Domestic route planning assistance
• Regional travel information
• Various destination options
• Multiple departure points

🌐 **CROSS-BORDER TRAVEL:**
• International travel planning
• Border crossing information
• Global destination options
• International route assistance

✈️ **SERVICE LEVEL OPTIONS:**
• Different service categories
• Various amenity options
• Multiple comfort levels
• Different pricing structures

🌅 **COASTAL ROUTE TRAVEL:**
• Coastal destination planning
• Beach route information
• Oceanfront travel options
• Seaside destination assistance

🔄 **FLEXIBLE TRAVEL PLANNING:**
• Various booking timeframes
• Different flexibility options
• Multiple date choices
• Various schedule options

📍 **ROUTE INFORMATION:**
• Common travel route details
• Popular destination information
• Frequent traveler routes
• Regular travel patterns

📋 **SERVICE FEATURES:**
• General service information
• Common travel amenities
• Standard service features
• Typical travel options

💡 *This service provides travel planning information and assistance.*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇸 Domestic", callback_data="travel_domestic"),
            types.InlineKeyboardButton("🌐 Cross-Border", callback_data="travel_crossborder")
        )
        markup.add(
            types.InlineKeyboardButton("✈️ Services", callback_data="travel_airtravel"),
            types.InlineKeyboardButton("🌅 Coastal", callback_data="travel_coastal")
        )
        markup.add(
            types.InlineKeyboardButton("📢 Join Updates", url="https://t.me/flights_bills_b4u"),
            types.InlineKeyboardButton("📞 Alt Contact", url="https://t.me/Eatsplugsus")
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
        f"Notification to {len(broadcast_users)} users\n\nPlease enter your travel update message:"
    )
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    # Prevent multiple broadcasts from same message
    if hasattr(message, 'is_broadcast_processed') and message.is_broadcast_processed:
        return
    message.is_broadcast_processed = True
    
    broadcast_text = message.text
    users = list(broadcast_users)
    success_count = 0
    fail_count = 0
    
    # Send initial status
    status_msg = bot.send_message(ADMIN_ID, f"Sending notification to {len(users)} users...")
    
    for user_id in users:
        try:
            notification = f"✈️ **Travel Update** ✈️\n\n{broadcast_text}\n\n*Travel planning information update*"
            bot.send_message(user_id, notification)
            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f"Notification delivery issue: {e}")
    
    # Update status
    bot.edit_message_text(
        f"Notification complete!\n\n"
        f"Successful: {success_count}\n"
        f"Unsuccessful: {fail_count}\n"
        f"Total recipients: {len(users)}",
        ADMIN_ID,
        status_msg.message_id
    )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    user_count = len(broadcast_users)
    bot.send_message(ADMIN_ID, f"Service statistics:\n\nUsers: {user_count}")

# ===== CHAT HANDLERS =====
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('hello'))
def hello_handler(message):
    user = message.from_user
    user_id = user.id
    
    # Add user to broadcast list
    broadcast_users.add(user_id)
    
    # Set chat state
    user_chat_states[user_id] = 'waiting_for_admin'
    
    user_info = f"User: {user.first_name} {user.last_name or ''} (@{user.username or 'No username'})"
    
    # Store message info for admin replies
    user_messages[message.message_id] = {
        'user_id': user.id,
        'user_info': user_info,
        'original_message': message.text
    }
    
    # Forward the "hello" message to admin with reply button
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📨 Reply", callback_data=f"reply_{message.message_id}"))
    
    forward_text = f"User greeting received\n\n{user_info}\nUser ID: {user.id}\n\nMessage: '{message.text}'"
    
    bot.send_message(ADMIN_ID, forward_text, reply_markup=keyboard)
    
    # Reply to the user
    bot.reply_to(message, "Hello! Our support team has been notified. They'll respond to you soon.\n\nYou can continue messaging here.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def reply_callback_handler(call):
    message_id = int(call.data.split('_')[1])
    
    if message_id in user_messages:
        user_data = user_messages[message_id]
        
        # Ask admin to type the reply
        msg = bot.send_message(ADMIN_ID, f"Response for user {user_data['user_info']}:")
        
        # Register next step handler for admin's reply
        bot.register_next_step_handler(msg, process_admin_reply, user_data['user_id'])
    else:
        bot.answer_callback_query(call.id, "Message information unavailable")

def process_admin_reply(message, user_id):
    try:
        # Send admin's reply to the user
        bot.send_message(user_id, f"📨 Support response:\n\n{message.text}")
        bot.reply_to(message, "Response delivered successfully!")
    except Exception as e:
        bot.reply_to(message, f"Response delivery issue: {str(e)}")

# Handler for forwarding user messages to admin
@bot.message_handler(func=lambda message: True)
def all_messages_handler(message):
    user = message.from_user
    user_id = user.id
    
    # Don't process admin's own messages
    if user_id == ADMIN_ID:
        return
    
    # Add user to broadcast list
    broadcast_users.add(user_id)
    
    # If user has started a chat, forward their messages to admin
    if user_chat_states.get(user_id) == 'waiting_for_admin' and message.text:
        user_info = f"User: {user.first_name} {user.last_name or ''} (@{user.username or 'No username'})"
        
        # Store message info
        user_messages[message.message_id] = {
            'user_id': user_id,
            'user_info': user_info,
            'original_message': message.text
        }
        
        # Forward message to admin with reply button
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📨 Reply", callback_data=f"reply_{message.message_id}"))
        
        forward_text = f"User message:\n\n{user_info}\nUser ID: {user_id}\n\nMessage: '{message.text}'"
        
        bot.send_message(ADMIN_ID, forward_text, reply_markup=keyboard)
        
        # Acknowledge user
        if not message.text.lower().startswith('hello'):
            bot.reply_to(message, "Message received. Support will respond soon.")

@app.route('/')
def home():
    # Copyright-safe landing page
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel Planning Assistance Service</title>
        <meta name="description" content="Travel planning information and assistance service providing general travel information">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .disclaimer { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div style="max-width: 600px; margin: 0 auto;">
            <h1>✈️ Travel Planning Assistance</h1>
            <p>General travel information and planning assistance</p>
            
            <div class="disclaimer">
                <p><strong>Disclaimer:</strong></p>
                <p>This service provides travel planning information and assistance.</p>
                <p>We are not affiliated with any specific travel providers.</p>
                <p>All information is for general planning purposes.</p>
            </div>
            
            <p>Status: <strong style="color:green">Service Active</strong></p>
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
        raise SystemExit("Service token required for operation")
    
    # Set webhook
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
            print(f"Service configured: {webhook_url}")
        else:
            print("Standard operation mode")
            
    except Exception as e:
        print(f"Configuration note: {e}")
    
    print("Travel planning assistance service active")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
