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

# ===== FLIGHT DATA WITH DISCOUNTS =====
FLIGHT_OFFERS = {
    "domestic": {
        "title": "🇺🇸 **Domestic Air Travel - Up to 50% Savings!**",
        "details": """**🔥 EXCLUSIVE DOMESTIC DEALS - UP TO 50% OFF!**

🚀 **HOT USA AIRLINE DEALS:**
• **American Airlines Routes**: Up to 50% discount on select routes
• **Delta Air Lines**: Special rates for domestic travel
• **United Airlines**: Exclusive member pricing available
• **Southwest Airlines**: Wanna Get Away fares with savings
• **JetBlue**: Mint & Core discounts on popular routes

📍 **MAJOR USA AIRLINES COVERED:**
✅ American Airlines (AA) - Premium service discounts
✅ Delta Air Lines (DL) - SkyMiles member rates
✅ United Airlines (UA) - MileagePlus exclusive deals
✅ Southwest Airlines (WN) - Low fare calendar access
✅ JetBlue Airways (B6) - TrueBlue point bonuses
✅ Alaska Airlines (AS) - West Coast specials
✅ Spirit Airlines (NK) - Ultra-low base fares
✅ Frontier Airlines (F9) - Discount Den member rates

💰 **CURRENT DISCOUNTS:**
• American Airlines: Up to 45% off select routes
• Delta: 30-50% off domestic flights
• United: Exclusive 40% savings codes
• Southwest: Wanna Get Away fares from $49
• JetBlue: 35% off + free checked bag offers

📅 **TRAVEL PERIODS:**
• Last Minute (0-7 days): Up to 50% off
• Short Term (8-21 days): 30-45% off
• Advance (22-90 days): 20-40% off
• Seasonal: Special holiday rates

🔒 **USA AIRLINE BENEFITS:**
✓ American AAdvantage miles
✓ Delta SkyMiles accrual
✓ United MileagePlus points
✓ Southwest Rapid Rewards
✓ JetBlue TrueBlue points"""
    },
    "crossborder": {
        "title": "🌐 **International Flights - USA Airlines Specials**",
        "details": """**🌎 INTERNATIONAL DISCOUNTS - USA AIRLINES GLOBAL NETWORK**

🚀 **USA AIRLINE INTERNATIONAL DEALS:**
• **American Airlines**: Transatlantic/Transpacific specials
• **Delta Air Lines**: SkyTeam global partner discounts
• **United Airlines**: Star Alliance international rates
• **International Routes**: Up to 40% off roundtrip

✈️ **USA AIRLINE ALLIANCES:**
• **American Airlines** (Oneworld Alliance)
• **Delta Air Lines** (SkyTeam Alliance)
• **United Airlines** (Star Alliance)
• Plus partner airline discounts

💰 **INTERNATIONAL SAVINGS:**
• Europe: Up to $500 off roundtrip
• Asia: 35-45% discount available
• Latin America: Special promo fares
• Canada: Cross-border deals up to 40% off"""
    },
    "airtravel": {
        "title": "✈️ **USA Airlines Service Classes - Discounted!**",
        "details": """**✈️ USA AIRLINE SERVICE LEVELS - ALL ON SALE!**

🏆 **FIRST CLASS (UP TO 50% OFF):**
• American Airlines Flagship First
• Delta Delta One Suites
• United Polaris Business
• Premium lie-flat seats discounted

🎯 **BUSINESS CLASS (UP TO 45% OFF):**
• American Business Class
• Delta Premium Select
• United Business Class
• International business deals

💺 **PREMIUM ECONOMY (UP TO 40% OFF):**
• American Premium Economy
• Delta Comfort+
• United Premium Plus
• Extra legroom, priority boarding

💰 **ECONOMY SAVERS (UP TO 60% OFF):**
• American Basic Economy
• Delta Main Cabin
• United Economy
• Lowest fare guarantees"""
    },
    "coastal": {
        "title": "🌅 **Coastal USA Airlines Routes - Beach Deals**",
        "details": """**🏖️ COASTAL USA AIRLINE ROUTES - SPECIAL RATES**

🚀 **WEST COAST USA AIRLINES:**
• **Los Angeles (LAX)**: American/Delta/United from $89
• **San Francisco (SFO)**: Alaska/United specials
• **Seattle (SEA)**: Delta hub discounts
• **San Diego (SAN)**: Southwest Wanna Get Away fares

🚀 **EAST COAST USA AIRLINES:**
• **New York (JFK/LGA)**: JetBlue/Delta/AA deals
• **Miami (MIA)**: American Airlines hub specials
• **Orlando (MCO)**: Southwest vacation packages
• **Boston (BOS)**: JetBlue hometown discounts

🏝️ **ISLAND DESTINATIONS:**
• Hawaii: United/Delta/AA inter-island deals
• Caribbean: American Airlines tropical routes
• Bahamas: JetBlue beach packages
• Florida Keys: Southwest Florida specials"""
    },
    "flexible": {
        "title": "🔄 **Last Minute USA Airline Deals - Up to 60% Off!**",
        "details": """**🎯 LAST MINUTE USA AIRLINE DISCOUNTS**

🚨 **EMERGENCY/LAST MINUTE (0-3 DAYS):**
• American Airlines: Up to 60% off unsold seats
• Delta Air Lines: Same-day departure deals
• United Airlines: Standby special rates
• Southwest: Close-in booking discounts

📅 **SHORT NOTICE (4-7 DAYS):**
• USA Airlines: 40-50% off remaining inventory
• Spirit/Frontier: Ultra-low last-minute fares
• JetBlue: Even More Space last-minute upgrades

💰 **FLEXIBLE DATE SAVINGS:**
• American Airlines: Flexible date calendar
• Delta: Date grid view for lowest fares
• United: Fare lock options available
• Southwest: Low fare calendar access"""
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
    
    # Impressive travel categories with discount mentions
    keyboard.add(types.InlineKeyboardButton("🇺🇸 USA Airlines up to 50% OFF", callback_data="travel_domestic"))
    keyboard.add(
        types.InlineKeyboardButton("🌐 International Deals", callback_data="travel_crossborder"),
        types.InlineKeyboardButton("✈️ Business Class Deals", callback_data="travel_airtravel")
    )
    keyboard.add(
        types.InlineKeyboardButton("🌅 Coastal Getaways", callback_data="travel_coastal"),
        types.InlineKeyboardButton("🔄 Last Minute Deals", callback_data="travel_flexible")
    )
    keyboard.add(types.InlineKeyboardButton("📍 Popular Routes", callback_data="travel_routes"))
    keyboard.add(types.InlineKeyboardButton("💰 Current Promotions", callback_data="travel_promotions"))
    
    # Contact & Channel
    button_channel = types.InlineKeyboardButton("📢 Join Exclusive Deals", url="https://t.me/flights_bills_b4u")
    button_contact1 = types.InlineKeyboardButton("💬 Book Now", url="https://t.me/yrfrnd_spidy")
    button_contact2 = types.InlineKeyboardButton("📞 Instant Support", url="https://t.me/Eatsplugsus")
    
    keyboard.add(button_channel)
    keyboard.add(button_contact1, button_contact2)

    # IMPRESSIVE START MESSAGE WITH DISCOUNTS & USA AIRLINES
    message_text = (
        "✨ **EXCLUSIVE FLIGHT DEALS UNLOCKED!** ✨\n\n"
        
        "🎉 **WELCOME TO USA AIRLINES DISCOUNT HUB!** 🎉\n\n"
        
        "🔥 **LIMITED TIME OFFERS:**\n"
        "✅ *UP TO 50% OFF* American Airlines, Delta, United & More!\n"
        "✅ *UP TO 60% OFF* Last Minute Flights\n"
        "✅ *EXCLUSIVE DEALS* Not Available Publicly\n"
        "✅ *BUSINESS CLASS* Up to 45% Discount\n"
        "✅ *INSTANT SAVINGS* on All USA Airlines\n\n"
        
        "🇺🇸 **MAJOR USA AIRLINES COVERED:**\n"
        "• American Airlines (AA) - Up to 50% OFF\n"
        "• Delta Air Lines (DL) - SkyMiles Specials\n"
        "• United Airlines (UA) - Exclusive Member Rates\n"
        "• Southwest Airlines (WN) - Wanna Get Away Fares\n"
        "• JetBlue Airways (B6) - Mint Class Discounts\n"
        "• Alaska Airlines (AS) - West Coast Deals\n"
        "• Spirit Airlines (NK) - Ultra Low Fares\n"
        "• Frontier Airlines (F9) - Discount Den Rates\n\n"
        
        "💰 **IMMEDIATE SAVINGS AVAILABLE:**\n"
        "📍 Domestic Routes: Up to 50% OFF\n"
        "📍 International: Up to $500 OFF\n"
        "📍 Business Class: Up to 45% OFF\n"
        "📍 Last Minute: Up to 60% OFF\n"
        "📍 Coastal Routes: Special Beach Rates\n\n"
        
        "🚀 **HOW IT WORKS:**\n"
        "1. Select your travel category below\n"
        "2. View exclusive USA airline discounts\n"
        "3. Contact our team for booking\n"
        "4. Save BIG on your next flight!\n\n"
        
        "⚠️ *Limited availability. Prices subject to change.*\n"
        "📞 *Contact us within 24 hours for best rates!*\n\n"
        
        "👇 **SELECT A CATEGORY TO VIEW DISCOUNTS:**"
    )

    bot.send_message(message.chat.id, message_text, reply_markup=keyboard, parse_mode='Markdown')

# ===== ENHANCED TRAVEL HANDLERS WITH DISCOUNTS =====
@bot.callback_query_handler(func=lambda call: call.data.startswith('travel_'))
def travel_handler(call):
    """Handle travel category clicks - show USA airline discounts"""
    user_id = call.from_user.id
    option = call.data.replace('travel_', '')
    
    if option in FLIGHT_OFFERS:
        offer = FLIGHT_OFFERS[option]
        
        # Enhanced response with urgency
        urgency = "🚨 *LIMITED TIME OFFER - PRICES MAY INCREASE SOON!*\n\n"
        response = f"{offer['title']}\n\n{urgency}{offer['details']}"
        
        # Action buttons with urgency
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔥 BOOK NOW - SAVE UP TO 50%", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Join Exclusive Deals", url="https://t.me/flights_bills_b4u")
        )
        markup.add(
            types.InlineKeyboardButton("💳 Apply Discount Code", callback_data="discount_code"),
            types.InlineKeyboardButton("✈️ More USA Airline Deals", callback_data="travel_more")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "routes":
        # Enhanced routes with USA airlines
        response = """📍 **POPULAR USA AIRLINE ROUTES - DISCOUNTED!**

🔥 **TOP DISCOUNTED ROUTES:**

🇺🇸 **AMERICAN AIRLINES (UP TO 50% OFF):**
• JFK → LAX: From $189 (Normally $379)
• MIA → ORD: From $129 (Normally $259)
• DFW → LAS: From $99 (Normally $199)
• PHX → SEA: From $149 (Normally $299)

✈️ **DELTA AIR LINES (UP TO 45% OFF):**
• ATL → MCO: From $79 (Normally $159)
• DTW → FLL: From $109 (Normally $219)
• SLC → DEN: From $89 (Normally $179)
• MSP → PHX: From $139 (Normally $279)

🛫 **UNITED AIRLINES (UP TO 40% OFF):**
• EWR → SFO: From $199 (Normally $399)
• IAH → LAX: From $149 (Normally $299)
• DEN → IAD: From $169 (Normally $339)
• ORD → MIA: From $119 (Normally $239)

💸 **SOUTHWEST AIRLINES WANNA GET AWAY:**
• DAL → HOU: From $49
• BWI → TPA: From $69
• MDW → STL: From $59
• PHX → SAN: From $79

🎯 **JETBLUE DISCOUNT ROUTES:**
• BOS → FLL: From $89 (Normally $179)
• JFK → AUA: From $199 (Normally $399)
• LGA → RDU: From $79 (Normally $159)

🏝️ **HAWAII SPECIALS:**
• Mainland → HNL: United/Delta from $299
• Inter-island: Hawaiian Airlines from $49

💰 *All prices one-way. Roundtrip doubles savings!*
🚨 *Limited seats at these prices!*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇸 American Airlines Deals", callback_data="travel_domestic"),
            types.InlineKeyboardButton("✈️ Delta Specials", callback_data="travel_airtravel")
        )
        markup.add(
            types.InlineKeyboardButton("🔥 BOOK NOW", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Join Deals", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "features":
        response = """📋 **USA AIRLINE BENEFITS & DISCOUNTS**

🏆 **PREMIUM BENEFITS INCLUDED:**

✅ **AMERICAN AIRLINES AADVANTAGE:**
• Earn miles on discounted fares
• Elite status qualifying dollars
• Priority boarding available
• Main Cabin Extra discounts

✅ **DELTA SKYMILES BENEFITS:**
• Mile accrual on all fares
• Medallion Qualification Dollars
• Sky Priority access options
• Comfort+ upgrade discounts

✅ **UNITED MILEAGEPLUS:**
• Premier qualifying points
• Economy Plus discounted access
• Priority boarding included
• Partner airline mileage earning

✅ **SOUTHWEST RAPID REWARDS:**
• Points earning on Wanna Get Away
• Companion Pass qualifying flights
• No change fees on all fares
• Two free checked bags always

✅ **JETBLUE TRUEBLUE:**
• Points never expire
• Mosaic status benefits
• Even More Space discounts
• Free high-speed wifi

💰 **ADDITIONAL DISCOUNTS:**
• Military/Government: Additional 5-10% off
• Senior Citizens: Special senior fares
• Students: Extra 5% discount
• Group Travel (6+): Up to 15% off

🎁 **LOYALTY BONUSES:**
• First booking: Extra 500 bonus miles
• Roundtrip bookings: Additional 5% off
• Weekend travel: Special weekend rates
• Holiday packages: Bundle discounts

💎 **BEST VALUE TIPS:**
1. Book Tuesday-Thursday for lowest fares
2. Use our exclusive discount codes
3. Combine with hotel for extra savings
4. Sign up for airline newsletters for flash sales

*Contact us for personalized discount codes!*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✈️ Business Class Deals", callback_data="travel_airtravel"),
            types.InlineKeyboardButton("🔄 Last Minute", callback_data="travel_flexible")
        )
        markup.add(
            types.InlineKeyboardButton("🔥 GET DISCOUNT CODE", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Exclusive Deals", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "promotions":
        response = """🔥 **CURRENT USA AIRLINE PROMOTIONS**

🎉 **JANUARY FLASH SALE - ENDS SOON!**

🇺🇸 **AMERICAN AIRLINES:**
• CODE: AA50JAN - 50% off select routes
• CODE: AABIZ25 - 25% off business class
• CODE: AAADV30 - 30% advance purchase

✈️ **DELTA AIR LINES:**
• CODE: DL45OFF - 45% domestic flights
• CODE: DLSKY35 - 35% SkyTeam routes
• CODE: DLMED20 - 20% off medical travel

🛫 **UNITED AIRLINES:**
• CODE: UA40SAVE - 40% off roundtrip
• CODE: UAPOLARIS - 30% off Polaris
• CODE: UAEMER - 15% emergency travel

💸 **SOUTHWEST AIRLINES:**
• Wanna Get Away fares from $49
• Companion Pass specials
• No hidden fees guarantee

🎯 **JETBLUE:**
• CODE: JBLUE30 - 30% off Mint
• CODE: JBBAGFREE - Free checked bag
• TrueBlue point bonuses 2x

🏝️ **HAWAIIAN AIRLINES:**
• CODE: HA40OFF - 40% off Hawaii
• CODE: HAMAINLAND - $299 mainland

💰 **LIMITED TIME OFFERS:**
• Book within 24 hours: Extra 5% off
• Roundtrip bookings: Additional 10% off
• Group of 4+: 15% group discount
• First-time users: $50 credit

⚠️ **PROMOTION TERMS:**
• Limited seats available
• Blackout dates may apply
• Minimum stay requirements
• Codes valid 48 hours only

🎁 **BONUS: Free hotel night with any flight over $300!**

*Contact us to apply these codes!*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇸 Apply AA50JAN Code", callback_data="travel_domestic"),
            types.InlineKeyboardButton("✈️ Use DL45OFF", callback_data="travel_airtravel")
        )
        markup.add(
            types.InlineKeyboardButton("🔥 GET ALL CODES", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Join for New Codes", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "more":
        # Show all USA airline deals
        response = """✈️ **ALL USA AIRLINE DISCOUNT CATEGORIES**

🇺🇸 **DOMESTIC USA AIRLINES - UP TO 50% OFF:**
• American Airlines exclusive rates
• Delta Air Lines member specials
• United Airlines discount codes
• Southwest low fare calendar
• JetBlue Mint class deals
• Alaska West Coast specials
• Spirit ultra-low base fares
• Frontier Discount Den rates

🌐 **INTERNATIONAL DISCOUNTS:**
• American Airlines global routes
• Delta SkyTeam worldwide
• United Star Alliance network
• International partner airlines

🏆 **PREMIUM CABIN SAVINGS:**
• First Class up to 50% off
• Business Class up to 45% off
• Premium Economy up to 40% off
• Main Cabin Extra discounts

🌅 **COASTAL & BEACH ROUTES:**
• Florida vacation specials
• California coastal deals
• Hawaii inter-island rates
• Caribbean all-inclusive

🔄 **FLEXIBLE TRAVEL OPTIONS:**
• Last minute up to 60% off
• Emergency travel discounts
• Standby special rates
• Date change flexibility

📍 **POPULAR ROUTE DEALS:**
• Transcontinental discounts
• Hub-to-hub specials
• Vacation route packages
• Business travel rates

💰 **CURRENT PROMOTIONS:**
• Flash sale codes active
• Limited time discounts
• Bonus mile offers
• Bundle savings

💎 **WHY BOOK WITH US:**
1. Exclusive rates not on public sites
2. Direct USA airline partnerships
3. Discount codes for extra savings
4. Personalized booking assistance
5. 24/7 customer support
6. Best price guarantee

🚨 **ACT NOW - LIMITED SEATS AVAILABLE!**

*Contact us within 24 hours for maximum savings!*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇸 Domestic Deals", callback_data="travel_domestic"),
            types.InlineKeyboardButton("🌐 International", callback_data="travel_crossborder")
        )
        markup.add(
            types.InlineKeyboardButton("✈️ Business Class", callback_data="travel_airtravel"),
            types.InlineKeyboardButton("🌅 Coastal", callback_data="travel_coastal")
        )
        markup.add(
            types.InlineKeyboardButton("🔥 INSTANT BOOKING", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Live Deals", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "discount_code":
        response = """🎫 **DISCOUNT CODE INSTRUCTIONS**

✅ **HOW TO USE DISCOUNT CODES:**

1. **Select your flight route** from our deals
2. **Contact our booking agent** via button below
3. **Provide the discount code** you want to use
4. **Agent will apply** the best available discount
5. **Confirm your booking** at discounted rate

🔥 **CURRENT ACTIVE CODES:**
• AA50JAN - American Airlines 50% off
• DL45OFF - Delta 45% domestic
• UA40SAVE - United 40% roundtrip
• JBLUE30 - JetBlue 30% Mint
• WANNA49 - Southwest $49 fares

⚠️ **CODE TERMS:**
• One code per booking
• Valid for 48 hours only
• Limited seats per code
• Subject to availability

💰 **EXTRA SAVINGS TIP:**
Combine with our "Book within 24 hours" bonus for additional 5% off!

🎁 **NEW USER BONUS:**
First-time customers get additional $25 credit!

👇 **CONTACT AGENT TO APPLY CODES:**"""
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 APPLY DISCOUNT NOW", url="https://t.me/yrfrnd_spidy"))
        markup.add(types.InlineKeyboardButton("📞 ALTERNATE AGENT", url="https://t.me/Eatsplugsus"))
        
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
        f"🚨 FLASH SALE ALERT TO {len(broadcast_users)} USERS!\n\n"
        f"Send your USA airline discount announcement:"
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
    status_msg = bot.send_message(ADMIN_ID, f"🚀 Sending USA airline deals to {len(users)} users...")
    
    for user_id in users:
        try:
            notification = (
                "🔥 **USA AIRLINES FLASH SALE!** 🔥\n\n"
                f"{broadcast_text}\n\n"
                "🇺🇸 *American, Delta, United & More*\n"
                "💰 *Discounts up to 50% OFF*\n"
                "🚨 *Limited time offer!*\n\n"
                "Book now before prices increase!"
            )
            bot.send_message(user_id, notification)
            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f"Notification delivery issue: {e}")
    
    # Update status
    bot.edit_message_text(
        f"✅ BROADCAST COMPLETE!\n\n"
        f"📊 Results:\n"
        f"• Successful: {success_count} users\n"
        f"• Failed: {fail_count} users\n"
        f"• Total: {len(users)} recipients\n\n"
        f"💰 Potential bookings: ${success_count * 200}+",
        ADMIN_ID,
        status_msg.message_id
    )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    user_count = len(broadcast_users)
    bot.send_message(
        ADMIN_ID,
        f"📊 **USA AIRLINES BOT STATISTICS**\n\n"
        f"👥 Total Users: {user_count}\n"
        f"💰 Potential Revenue: ${user_count * 200}\n"
        f"🚀 Active Offers: 8 USA airlines\n"
        f"🎫 Discount Codes: 12 active\n"
        f"📈 Growth Rate: +{min(user_count, 50)} today"
    )

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
    keyboard.add(types.InlineKeyboardButton("📨 Reply with Discount", callback_data=f"reply_{message.message_id}"))
    
    forward_text = (
        f"👋 NEW USER INQUIRY - USA AIRLINES\n\n"
        f"{user_info}\n"
        f"User ID: {user.id}\n\n"
        f"Message: '{message.text}'\n\n"
        f"💰 Offer: 50% discount on first booking!"
    )
    
    bot.send_message(ADMIN_ID, forward_text, reply_markup=keyboard)
    
    # Impressive reply to the user
    bot.reply_to(
        message,
        "🎉 **HELLO! WELCOME TO USA AIRLINES DISCOUNT CENTER!** 🎉\n\n"
        "🔥 **SPECIAL WELCOME OFFER JUST FOR YOU:**\n"
        "✅ **EXTRA 10% OFF** your first booking!\n"
        "✅ **PRIORITY ACCESS** to flash sales\n"
        "✅ **PERSONAL DISCOUNT CODE** generated\n\n"
        "Our USA airline specialist will contact you shortly with your personalized discount!\n\n"
        "*Limited to first 24 hours only!*"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def reply_callback_handler(call):
    message_id = int(call.data.split('_')[1])
    
    if message_id in user_messages:
        user_data = user_messages[message_id]
        
        # Ask admin to type the reply
        msg = bot.send_message(
            ADMIN_ID,
            f"💬 REPLY TO USER {user_data['user_info']}\n\n"
            f"✨ **OFFER SUGGESTION:** Include a discount code!\n"
            f"💎 **TEMPLATE:** 'Hi! Here's AA50JAN code for 50% off...'\n\n"
            f"Type your reply with discount offer:"
        )
        
        # Register next step handler for admin's reply
        bot.register_next_step_handler(msg, process_admin_reply, user_data['user_id'])
    else:
        bot.answer_callback_query(call.id, "Message information unavailable")

def process_admin_reply(message, user_id):
    try:
        # Send admin's reply to the user
        bot.send_message(
            user_id,
            f"🎫 **USA AIRLINES DISCOUNT OFFER** 🎫\n\n"
            f"{message.text}\n\n"
            f"💰 *This offer is exclusive to you!*\n"
            f"⏰ *Valid for 24 hours only!*\n\n"
            f"Reply 'BOOK' to confirm your discount!"
        )
        bot.reply_to(message, "✅ DISCOUNT OFFER DELIVERED! User received exclusive USA airline deal!")
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
        keyboard.add(types.InlineKeyboardButton("🎫 Reply with USA Airline Deal", callback_data=f"reply_{message.message_id}"))
        
        forward_text = (
            f"📩 USER MESSAGE - USA AIRLINES BOT\n\n"
            f"{user_info}\n"
            f"User ID: {user_id}\n\n"
            f"Message: '{message.text}'\n\n"
            f"💡 **Suggestion:** Offer AA/DL/UA discount code"
        )
        
        bot.send_message(ADMIN_ID, forward_text, reply_markup=keyboard)
        
        # Acknowledge user
        if not message.text.lower().startswith('hello'):
            bot.reply_to(
                message,
                "✅ **MESSAGE RECEIVED!** ✅\n\n"
                "Our USA airline specialist is preparing your personalized discount offer!\n\n"
                "✨ **BONUS:** You'll receive an extra discount code for quick response!"
            )

@app.route('/')
def home():
    # Simple landing page without heavy SEO optimization
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flight Discounts Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .status {
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                display: inline-block;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✈️ Flight Discounts Bot</h1>
            <p>Get exclusive discounts on USA airline flights</p>
            
            <div class="status">✅ Bot is Active</div>
            
            <h3>Available Airlines:</h3>
            <p>American Airlines • Delta • United • Southwest • JetBlue • Alaska • Spirit • Frontier</p>
            
            <h3>Current Offers:</h3>
            <p>• Up to 50% off domestic flights</p>
            <p>• Up to 60% off last minute deals</p>
            <p>• Business class discounts up to 45%</p>
            
            <p style="margin-top: 30px;">
                Use our Telegram bot for real-time deals and discounts!
            </p>
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
            print(f"USA Airlines Bot deployed: {webhook_url}")
        else:
            print("USA Airlines Bot running in polling mode")
            
    except Exception as e:
        print(f"Webhook configuration: {e}")
    
    print("🚀 USA Airlines Discount Bot ACTIVE!")
    print("🇺🇸 Serving: American, Delta, United, Southwest, JetBlue & more")
    print("💰 Discounts: Up to 50% OFF major USA airlines")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
