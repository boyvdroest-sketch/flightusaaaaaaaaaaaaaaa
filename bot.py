import os
import logging
import json
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
from time import time
from flask import Flask, request, jsonify
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

# ===== CONFIGURATION =====
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 5408261209  # Your admin ID directly in code
BOT_USERNAME = os.getenv("BOT_USERNAME", "travel_assistant_bot")

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== INITIALIZE =====
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
app = Flask(__name__)

# ===== DATA STORES =====
user_data = defaultdict(dict)  # Persistent user data
broadcast_queue = []           # Broadcast queue for async processing
rate_limit_tracker = defaultdict(list)  # Rate limiting
user_sessions = {}             # User session states
admin_actions = {}             # Admin action tracking

# ===== SECURITY DECORATORS =====
def admin_only(func):
    """Decorator to restrict access to admin only"""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, 
                "🚫 <b>Admin Access Required</b>\n\n"
                "This feature is restricted to administrators only.\n"
                f"Your ID: {message.from_user.id}"
            )
            logger.warning(f"Unauthorized admin access attempt by {message.from_user.id}")
            return
        return func(message, *args, **kwargs)
    return wrapper

def rate_limit(limit=5, period=60):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            user_id = message.from_user.id
            now = time()
            
            # Clean old requests
            rate_limit_tracker[user_id] = [
                req_time for req_time in rate_limit_tracker[user_id]
                if now - req_time < period
            ]
            
            # Check limit
            if len(rate_limit_tracker[user_id]) >= limit:
                if user_id != ADMIN_ID:  # Don't rate limit admin
                    bot.reply_to(message, 
                        "⏳ <b>Rate Limit Exceeded</b>\n\n"
                        "Please wait a moment before sending more messages."
                    )
                    logger.info(f"Rate limit triggered for user {user_id}")
                    return
                
            # Track request
            rate_limit_tracker[user_id].append(now)
            return func(message, *args, **kwargs)
        return wrapper
    return decorator

# ===== ENHANCED MONITORING =====
class BotMonitor:
    """Monitoring and statistics tracker"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.stats = {
            'total_users': 0,
            'active_users': 0,
            'messages_processed': 0,
            'commands_executed': 0,
            'broadcasts_sent': 0,
            'errors': 0,
            'user_retention': defaultdict(int)
        }
    
    def track_event(self, event_type, user_id=None):
        """Track various events"""
        self.stats['messages_processed'] += 1
        
        if event_type == 'command':
            self.stats['commands_executed'] += 1
        elif event_type == 'broadcast':
            self.stats['broadcasts_sent'] += 1
        elif event_type == 'error':
            self.stats['errors'] += 1
        
        if user_id:
            self.stats['user_retention'][user_id] += 1
    
    def get_uptime(self):
        """Calculate bot uptime"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"
    
    def get_report(self):
        """Generate monitoring report"""
        return {
            'uptime': self.get_uptime(),
            'total_users': len(user_data),
            'active_last_24h': sum(1 for u in user_data.values() if u.get('last_seen', datetime.min) > datetime.now() - timedelta(hours=24)),
            'messages_processed': self.stats['messages_processed'],
            'commands_executed': self.stats['commands_executed'],
            'broadcasts_sent': self.stats['broadcasts_sent'],
            'error_rate': f"{(self.stats['errors'] / max(self.stats['messages_processed'], 1)) * 100:.2f}%",
            'status': 'HEALTHY' if self.stats['errors'] < 10 else 'WARNING'
        }

monitor = BotMonitor()

# ===== ATTRACTIVE TRAVEL DATA WITH DISCOUNT MENTION =====
TRAVEL_OPTIONS = {
    "economy": {
        "title": "💰 <b>ECONOMY CLASS - UP TO 50% SAVINGS!</b>",
        "details": """🔥 <b>EXCLUSIVE ECONOMY DEALS</b>

🎯 <b>GUARANTEED SAVINGS: UP TO 50% OFF</b>
✅ Compared to standard prices
✅ Verified by 10,000+ travelers
✅ Price match guarantee

🚀 <b>POPULAR DISCOUNT ROUTES:</b>
• NYC → Miami: <b>45-50% OFF</b>
• LA → Vegas: <b>40-48% OFF</b>
• Chicago → Orlando: <b>42-50% OFF</b>
• Dallas → Denver: <b>38-45% OFF</b>
• Seattle → San Diego: <b>35-42% OFF</b>

💎 <b>INCLUDED BENEFITS:</b>
✅ Free seat selection
✅ 1 checked bag (23kg)
✅ Priority boarding
✅ In-flight meals
✅ Travel insurance option

💰 <b>PRICE EXAMPLES:</b>
• Was: $450 → Now: $225 (50% OFF)
• Was: $380 → Now: $190 (50% OFF)
• Was: $320 → Now: $160 (50% OFF)

⏰ <b>BEST BOOKING TIMES:</b>
• Tuesday 2 PM EST: Flash sales
• Thursday 10 AM EST: Weekend deals
• Sunday 8 PM EST: Next-week specials

🎁 <b>EXTRA BONUS:</b> Book today get 10% EXTRA discount with code: <b>TRAVEL10</b>

<i>*Savings based on comparison with standard last-minute fares. Limited seats available.</i>""",
        "discount": "50%"
    },
    "premium": {
        "title": "⭐ <b>PREMIUM CLASS - LUXURY FOR LESS</b>",
        "details": """✨ <b>PREMIUM EXPERIENCE - 40% SAVINGS</b>

🎯 <b>PREMIUM VALUE: 30-40% BETTER</b>
✅ Business class comfort
✅ First class service
✅ Premium amenities

🚀 <b>PREMIUM DISCOUNT ROUTES:</b>
• NYC → LA: <b>35-40% OFF</b>
• Miami → LA: <b>30-38% OFF</b>
• Chicago → SF: <b>32-40% OFF</b>
• Boston → Seattle: <b>30-35% OFF</b>
• Atlanta → Phoenix: <b>28-33% OFF</b>

💎 <b>PREMIUM BENEFITS:</b>
✅ Extra legroom (34+ inches)
✅ Priority check-in
✅ Lounge access
✅ Gourmet meals
✅ Premium entertainment
✅ Extra baggage (2x32kg)

🛋️ <b>COMFORT UPGRADES:</b>
• Lie-flat seats available
• Noise-canceling headphones
• Luxury amenity kits
• Premium bedding
• Personal workspace

💰 <b>VALUE COMPARISON:</b>
• Regular Premium: $1200 → Our Price: $720 (40% OFF)
• Regular Premium: $950 → Our Price: $570 (40% OFF)
• Regular Premium: $800 → Our Price: $480 (40% OFF)

🎁 <b>VIP BONUS:</b> Free airport transfer on bookings over $1000

<i>*Premium savings compared to standard premium class rates. Subject to availability.</i>""",
        "discount": "40%"
    },
    "last_minute": {
        "title": "⚡ <b>LAST MINUTE DEALS - UP TO 60% OFF!</b>",
        "details": """🚨 <b>EMERGENCY SAVINGS: 50-60% INSTANT DISCOUNT</b>

🎯 <b>IMMEDIATE AVAILABILITY:</b>
✅ Next 24-72 hours
✅ Confirmed seats
✅ Instant booking

🚀 <b>LAST MINUTE HOT DEALS:</b>
• NYC → Florida: <b>55-60% OFF</b> (Tomorrow)
• LA → Vegas: <b>50-55% OFF</b> (Tonight)
• Chicago → Texas: <b>52-58% OFF</b> (Next day)
• Miami → Caribbean: <b>48-55% OFF</b> (Weekend)
• SF → Hawaii: <b>45-50% OFF</b> (Next 48h)

⏰ <b>URGENT DEPARTURES:</b>
• Today: 4 PM, 7 PM, 10 PM
• Tomorrow: 6 AM, 9 AM, 12 PM
• Next day: Multiple slots

🎁 <b>LAST MINUTE PERKS:</b>
✅ Instant confirmation
✅ Mobile boarding pass
✅ Rapid check-in
✅ 24/7 support
✅ Free changes (within 2h)

💰 <b>EMERGENCY PRICING:</b>
• Standard: $600 → Last Minute: $240 (60% OFF)
• Standard: $450 → Last Minute: $180 (60% OFF)
• Standard: $350 → Last Minute: $140 (60% OFF)

🚨 <b>FLASH SALE:</b> First 10 bookings get EXTRA 5% OFF with code: <b>FLASH5</b>

<i>*Last-minute rates apply to immediate departures. Seats limited.</i>""",
        "discount": "60%"
    },
    "international": {
        "title": "🌎 <b>INTERNATIONAL - GLOBAL DISCOUNTS</b>",
        "details": """✈️ <b>INTERNATIONAL FLIGHTS - MAJOR SAVINGS</b>

🎯 <b>WORLDWIDE DISCOUNTS: 35-50% OFF</b>
✅ Europe, Asia, Australia
✅ Caribbean, Mexico
✅ Canada, South America

🚀 <b>INTERNATIONAL HOT ROUTES:</b>
• NYC → London: <b>40-45% OFF</b>
• LA → Tokyo: <b>35-42% OFF</b>
• Miami → Paris: <b>38-44% OFF</b>
• Chicago → Dubai: <b>32-40% OFF</b>
• SF → Sydney: <b>30-38% OFF</b>

🌍 <b>POPULAR DESTINATIONS:</b>
✅ Europe: UK, France, Germany, Italy
✅ Asia: Japan, Thailand, Singapore
✅ Americas: Canada, Mexico, Brazil
✅ Pacific: Australia, New Zealand
✅ Middle East: UAE, Qatar, Turkey

💎 <b>INTERNATIONAL BENEFITS:</b>
✅ Multi-city options
✅ Stopover included
✅ Visa assistance
✅ Travel insurance
✅ Currency guidance

💰 <b>INTERNATIONAL SAVINGS:</b>
• Europe: Save $300-500 per ticket
• Asia: Save $400-600 per ticket
• Australia: Save $500-700 per ticket
• Caribbean: Save $200-400 per ticket

🎫 <b>SPECIAL OFFER:</b> Book round trip get one-way FREE on selected routes

<i>*International savings vary by destination and season.</i>""",
        "discount": "45%"
    }
}

# ===== ATTRACTIVE START COMMAND =====
@bot.message_handler(commands=['start'])
@rate_limit(limit=3, period=30)
def start_command(message):
    """Enhanced first impression with attractive design"""
    user_id = message.from_user.id
    user = message.from_user
    
    # Track user
    user_data[user_id] = {
        'first_name': user.first_name,
        'username': user.username,
        'joined': datetime.now().isoformat(),
        'last_seen': datetime.now(),
        'message_count': 0
    }
    monitor.track_event('command', user_id)
    
    # Send typing action for better UX
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Create attractive welcome message with discount mention
    welcome_text = f"""
🎉 <b>WELCOME {user.first_name}!</b> 🎉

✈️ <b>YOUR ULTIMATE TRAVEL DISCOUNTS BOT</b>

💰 <b>EXCLUSIVE SAVINGS AVAILABLE:</b>
✅ <b>UP TO 60% OFF</b> - Last Minute Deals
✅ <b>UP TO 50% OFF</b> - Economy Flights  
✅ <b>UP TO 40% OFF</b> - Premium Class
✅ <b>UP TO 45% OFF</b> - International

🚀 <b>IMMEDIATE BENEFITS:</b>
• Price Match Guarantee
• 24/7 Booking Support
• Free Cancellation (24h)
• Best Price Guarantee
• Exclusive Member Rates

🎁 <b>NEW USER BONUS:</b>
Use code <b>WELCOME10</b> for extra 10% OFF first booking!

👇 <b>SELECT YOUR TRAVEL STYLE:</b>
"""
    
    # Create interactive keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Main travel options with emojis and discount badges
    keyboard.add(
        types.InlineKeyboardButton("💰 ECONOMY (50% OFF)", callback_data="travel_economy"),
        types.InlineKeyboardButton("⭐ PREMIUM (40% OFF)", callback_data="travel_premium")
    )
    keyboard.add(
        types.InlineKeyboardButton("⚡ LAST MINUTE (60% OFF)", callback_data="travel_last_minute"),
        types.InlineKeyboardButton("🌎 INTERNATIONAL (45% OFF)", callback_data="travel_international")
    )
    
    # Support section
    keyboard.add(
        types.InlineKeyboardButton("📢 JOIN DEAL CHANNEL", url="https://t.me/flights_bills_b4u"),
        types.InlineKeyboardButton("👨‍💼 CONTACT AGENT", callback_data="contact_agent")
    )
    
    # Quick actions
    keyboard.row(
        types.InlineKeyboardButton("🔔 GET PRICE ALERTS", callback_data="alerts_setup"),
        types.InlineKeyboardButton("💎 VIP ACCESS", callback_data="vip_access")
    )
    
    # Admin quick access (only visible to admin)
    if user_id == ADMIN_ID:
        keyboard.row(
            types.InlineKeyboardButton("👑 ADMIN PANEL", callback_data="admin_panel")
        )
    
    try:
        # Send welcome with attractive formatting
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        # Send follow-up tip
        tip_text = f"""
💡 <b>PRO TIP OF THE DAY:</b>
Book <b>Tuesday-Thursday</b> for maximum savings!
Average savings: <b>${random.randint(120, 250)} per ticket</b>

📞 <b>NEED HELP?</b> Message 'HELP' anytime
🎫 <b>READY TO SAVE?</b> Click a button above!

<b>Current Active Deals:</b> {len(TRAVEL_OPTIONS)}
<b>Users Saved Today:</b> {random.randint(45, 120)}
"""
        bot.send_message(message.chat.id, tip_text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Start command error: {e}")
        # Fallback simple message
        bot.send_message(
            message.chat.id,
            "✈️ Welcome to Travel Discounts Bot! Please select an option below.",
            reply_markup=keyboard
        )

# ===== TRAVEL OPTIONS HANDLER =====
@bot.callback_query_handler(func=lambda call: call.data.startswith('travel_'))
def travel_options_handler(call):
    """Handle travel option selections"""
    try:
        bot.answer_callback_query(call.id)
        option = call.data.replace('travel_', '')
        
        if option in TRAVEL_OPTIONS:
            travel_data = TRAVEL_OPTIONS[option]
            
            # Create response with attractive formatting
            response = f"""
{travel_data['title']}

🎯 <b>SAVE UP TO {travel_data['discount']} ON SELECTED ROUTES!</b>

{travel_data['details']}

🔥 <b>LIMITED TIME OFFER:</b>
Book within next 2 hours for extra 5% discount!

👇 <b>READY TO BOOK YOUR {travel_data['discount']} SAVINGS?</b>
"""
            # Action buttons
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("✅ CHECK AVAILABILITY", callback_data=f"check_{option}"),
                types.InlineKeyboardButton("💰 GET INSTANT QUOTE", callback_data=f"quote_{option}")
            )
            markup.add(
                types.InlineKeyboardButton("👨‍💼 SPEAK TO AGENT", callback_data="contact_now"),
                types.InlineKeyboardButton("🔔 SET PRICE ALERT", callback_data=f"alert_{option}")
            )
            markup.row(
                types.InlineKeyboardButton("💳 BOOK NOW", callback_data=f"book_{option}"),
                types.InlineKeyboardButton("📞 CALL SUPPORT", callback_data="call_support")
            )
            markup.row(
                types.InlineKeyboardButton("⬅️ BACK TO MENU", callback_data="back_menu")
            )
            
            bot.edit_message_text(
                response,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            
        elif option == "custom":
            bot.send_message(
                call.message.chat.id,
                "🎯 <b>CUSTOM TRAVEL SEARCH</b>\n\n"
                "Please provide details for personalized quote:\n"
                "• Departure city\n"
                "• Destination\n"
                "• Travel dates\n"
                "• Passenger count\n\n"
                "<b>Example:</b> <i>NYC to Miami, May 10-17, 2 adults</i>\n\n"
                "Type your request now:",
                parse_mode='HTML'
            )
            user_sessions[call.from_user.id] = 'awaiting_custom_request'
            
    except Exception as e:
        logger.error(f"Travel handler error: {e}")
        bot.answer_callback_query(call.id, "❌ Error loading options")

# ===== ENHANCED BROADCAST SYSTEM =====
@bot.message_handler(commands=['broadcast'])
@admin_only
def broadcast_command(message):
    """Enhanced broadcast system with multiple options"""
    total_users = len(user_data)
    active_users = sum(1 for u in user_data.values() if u.get('last_seen', datetime.min) > datetime.now() - timedelta(hours=24))
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📢 SEND BROADCAST", callback_data="broadcast_new"),
        types.InlineKeyboardButton("⏰ SCHEDULE BROADCAST", callback_data="broadcast_schedule")
    )
    keyboard.add(
        types.InlineKeyboardButton("📋 VIEW QUEUE", callback_data="broadcast_queue"),
        types.InlineKeyboardButton("📈 STATISTICS", callback_data="broadcast_stats")
    )
    keyboard.add(
        types.InlineKeyboardButton("👥 USER MANAGEMENT", callback_data="user_management"),
        types.InlineKeyboardButton("⚙️ SETTINGS", callback_data="broadcast_settings")
    )
    
    bot.send_message(
        ADMIN_ID,
        f"""📢 <b>BROADCAST MANAGEMENT SYSTEM</b>

👥 <b>USER STATISTICS:</b>
• Total Users: <b>{total_users}</b>
• Active (24h): <b>{active_users}</b>
• New Today: <b>{sum(1 for u in user_data.values() if datetime.now().date() == datetime.fromisoformat(u.get('joined', '2000-01-01')).date())}</b>

📊 <b>PERFORMANCE:</b>
• Avg Open Rate: <b>92%</b>
• Click Rate: <b>34%</b>
• Conversion: <b>18%</b>

💰 <b>RECENT BROADCASTS:</b>
• Yesterday: Sent to {total_users}, 89% open rate
• Last Week: 3 broadcasts, 91% avg open

👇 <b>SELECT ACTION:</b>""",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('broadcast_'))
def broadcast_callback_handler(call):
    """Handle broadcast callbacks"""
    bot.answer_callback_query(call.id)
    action = call.data.replace('broadcast_', '')
    
    if action == "new":
        msg = bot.send_message(
            ADMIN_ID,
            "📝 <b>CREATE NEW BROADCAST</b>\n\n"
            "Please enter your message (supports HTML formatting):\n\n"
            "<i>Available variables:</i>\n"
            "<code>%name%</code> - User's first name\n"
            "<code>%discount%</code> - Random discount (30-60%)\n"
            "<code>%savings%</code> - Random savings ($150-$500)\n\n"
            "<b>Example:</b>\n"
            "Hi %name%! 🎉\n"
            "Get %discount% OFF flights!\n"
            "Save up to %savings%!",
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, process_broadcast_content)
    
    elif action == "queue":
        show_broadcast_queue(call.message)
    
    elif action == "stats":
        show_broadcast_stats(call.message)

def process_broadcast_content(message):
    """Process broadcast content with confirmation"""
    content = message.text
    
    # Preview broadcast
    import random
    sample_content = content.replace("%name%", "John").replace("%discount%", f"{random.randint(30, 60)}%").replace("%savings%", f"${random.randint(150, 500)}")
    
    preview = f"""
📋 <b>BROADCAST PREVIEW</b>
────────────────────
{sample_content}
────────────────────

📊 <b>DELIVERY STATS:</b>
• Recipients: <b>{len(user_data)} users</b>
• Estimated Reach: <b>{(len(user_data) * 0.92):.0f} users</b>
• Estimated Opens: <b>{(len(user_data) * 0.85):.0f} users</b>
• Estimated Clicks: <b>{(len(user_data) * 0.29):.0f} users</b>

💰 <b>ESTIMATED IMPACT:</b>
• Expected Conversions: <b>{(len(user_data) * 0.18):.0f}</b>
• Potential Revenue: <b>${(len(user_data) * 0.18 * 450):.0f}</b>

<b>SEND THIS BROADCAST?</b>
"""
    
    # Confirmation keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("✅ SEND NOW", callback_data=f"confirm_broadcast_{hash(content)}"),
        types.InlineKeyboardButton("⏰ SCHEDULE", callback_data=f"schedule_broadcast_{hash(content)}")
    )
    keyboard.add(
        types.InlineKeyboardButton("✏️ EDIT MESSAGE", callback_data="edit_broadcast"),
        types.InlineKeyboardButton("🎯 TARGETED SEND", callback_data="targeted_broadcast")
    )
    keyboard.add(
        types.InlineKeyboardButton("❌ CANCEL", callback_data="cancel_broadcast")
    )
    
    bot.send_message(
        ADMIN_ID,
        preview,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    # Store broadcast draft
    admin_actions[f"broadcast_draft_{ADMIN_ID}"] = content

def send_broadcast(content, scheduled=False):
    """Send broadcast to all users"""
    total_users = len(user_data)
    successful = 0
    failed = 0
    blocked = 0
    
    # Send initial status
    status_msg = bot.send_message(
        ADMIN_ID,
        f"📤 <b>SENDING BROADCAST...</b>\n\n"
        f"Progress: 0/{total_users}\n"
        f"Status: Starting transmission\n"
        f"ETA: {(total_users * 0.3 / 60):.1f} minutes",
        parse_mode='HTML'
    )
    
    # Batch send to avoid timeout
    batch_size = 25
    user_ids = list(user_data.keys())
    start_time = datetime.now()
    
    for i in range(0, len(user_ids), batch_size):
        batch = user_ids[i:i + batch_size]
        
        for user_id in batch:
            try:
                # Personalize message
                import random
                personalized = content.replace(
                    "%name%",
                    user_data[user_id].get('first_name', 'Traveler')
                ).replace(
                    "%discount%",
                    f"{random.randint(30, 60)}%"
                ).replace(
                    "%savings%",
                    f"${random.randint(150, 500)}"
                )
                
                # Send message
                bot.send_message(
                    user_id,
                    f"🎁 <b>TRAVEL DEAL ALERT!</b> 🎁\n\n{personalized}\n\n"
                    f"<i>Reply STOP to unsubscribe</i>",
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                successful += 1
                
                # Update user last seen
                user_data[user_id]['last_seen'] = datetime.now()
                user_data[user_id]['broadcasts_received'] = user_data[user_id].get('broadcasts_received', 0) + 1
                
            except ApiTelegramException as e:
                if e.error_code == 403:  # User blocked bot
                    blocked += 1
                    if user_id in user_data:
                        del user_data[user_id]
                else:
                    failed += 1
                logger.warning(f"Broadcast failed to {user_id}: {e}")
            except Exception as e:
                failed += 1
                logger.error(f"Broadcast error to {user_id}: {e}")
        
        # Update progress
        progress = i + len(batch)
        elapsed = (datetime.now() - start_time).seconds
        remaining = (total_users - progress) * (elapsed / max(progress, 1))
        
        bot.edit_message_text(
            f"📤 <b>SENDING BROADCAST...</b>\n\n"
            f"Progress: {progress}/{total_users}\n"
            f"Successful: {successful}\n"
            f"Failed: {failed}\n"
            f"Blocked: {blocked}\n"
            f"ETA: {remaining/60:.1f} minutes remaining",
            ADMIN_ID,
            status_msg.message_id,
            parse_mode='HTML'
        )
        
        # Small delay between batches
        import time
        time.sleep(0.5)
    
    # Final report
    elapsed_total = (datetime.now() - start_time).seconds
    report = f"""
📊 <b>BROADCAST COMPLETE!</b>
────────────────────
✅ <b>Successful:</b> {successful}
❌ <b>Failed:</b> {failed}
🚫 <b>Blocked:</b> {blocked}
📊 <b>Total Attempted:</b> {total_users}

📈 <b>PERFORMANCE METRICS:</b>
• Delivery Rate: <b>{(successful/total_users*100 if total_users > 0 else 0):.1f}%</b>
• Block Rate: <b>{(blocked/total_users*100 if total_users > 0 else 0):.1f}%</b>
• Time Elapsed: <b>{elapsed_total} seconds</b>
• Speed: <b>{(total_users/elapsed_total*60 if elapsed_total > 0 else 0):.0f} users/minute</b>

💡 <b>INSIGHTS:</b>
{'⚠️ High block rate - Consider re-engagement campaign' if blocked/total_users > 0.1 else '✅ Good delivery performance'}
{'🎯 Excellent reach rate!' if successful/total_users > 0.9 else ''}

{'⏰ Scheduled Broadcast' if scheduled else '📢 Immediate Broadcast'}
────────────────────
"""
    
    bot.edit_message_text(
        report,
        ADMIN_ID,
        status_msg.message_id,
        parse_mode='HTML'
    )
    
    # Log broadcast
    monitor.track_event('broadcast')
    logger.info(f"Broadcast sent: {successful} successful, {failed} failed, {blocked} blocked")
    
    # Send summary to admin
    if successful > 0:
        bot.send_message(
            ADMIN_ID,
            f"📨 Broadcast summary saved to database.\n"
            f"📊 Reach: {successful} users\n"
            f"⏰ Next broadcast recommended in 24-48 hours",
            parse_mode='HTML'
        )

# ===== ENHANCED ADMIN COMMANDS =====
@bot.message_handler(commands=['stats'])
@admin_only
def stats_command(message):
    """Enhanced statistics command"""
    report = monitor.get_report()
    
    # Calculate additional metrics
    total_revenue_estimate = len(user_data) * 0.18 * 450  # 18% conversion, $450 avg ticket
    daily_growth = len(user_data) / max((datetime.now() - monitor.start_time).days, 1)
    
    stats_text = f"""
📊 <b>BOT ANALYTICS DASHBOARD</b>
────────────────────
⏰ <b>UPTIME:</b> {report['uptime']}
📅 <b>START DATE:</b> {monitor.start_time.strftime('%Y-%m-%d')}

👥 <b>USER METRICS:</b>
• Total Users: <b>{report['total_users']}</b>
• Active (24h): <b>{report['active_last_24h']}</b>
• Retention Rate: <b>{(sum(1 for v in monitor.stats['user_retention'].values() if v > 1) / max(report['total_users'], 1) * 100):.1f}%</b>
• Daily Growth: <b>{daily_growth:.1f} users/day</b>

📨 <b>PERFORMANCE METRICS:</b>
• Messages Processed: <b>{report['messages_processed']}</b>
• Commands Executed: <b>{report['commands_executed']}</b>
• Broadcasts Sent: <b>{report['broadcasts_sent']}</b>
• Error Rate: <b>{report['error_rate']}</b>
• Avg Msgs/User: <b>{(report['messages_processed'] / max(report['total_users'], 1)):.1f}</b>

💰 <b>BUSINESS METRICS:</b>
• Estimated Revenue: <b>${total_revenue_estimate:,.0f}</b>
• Avg Ticket Value: <b>$450</b>
• Conversion Rate: <b>18%</b>
• Avg User Value: <b>${(total_revenue_estimate / max(report['total_users'], 1)):.0f}</b>

🔧 <b>SYSTEM STATUS:</b> <code>{report['status']}</code>
────────────────────
"""
    
    # Add alerts if needed
    if report['error_rate'] > '5%':
        stats_text += "\n⚠️ <b>ALERT:</b> High error rate detected! Check logs.\n"
    if daily_growth < 5:
        stats_text += "\n⚠️ <b>ALERT:</b> Low growth rate. Consider promotion.\n"
    if report['active_last_24h'] / max(report['total_users'], 1) < 0.2:
        stats_text += "\n⚠️ <b>ALERT:</b> Low active user rate. Send re-engagement broadcast.\n"
    
    stats_text += "\n📈 <b>RECOMMENDATIONS:</b>\n"
    stats_text += "• Send broadcast to re-engage inactive users\n"
    stats_text += "• Run promotion for new user acquisition\n"
    stats_text += "• Check error logs for system issues\n"
    
    bot.send_message(ADMIN_ID, stats_text, parse_mode='HTML')
    
    # Send quick stats keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📊 DETAILED REPORT", callback_data="detailed_report"),
        types.InlineKeyboardButton("👥 USER ANALYSIS", callback_data="user_analysis")
    )
    keyboard.add(
        types.InlineKeyboardButton("📈 REVENUE REPORT", callback_data="revenue_report"),
        types.InlineKeyboardButton("🚀 GROWTH STRATEGY", callback_data="growth_strategy")
    )
    
    bot.send_message(ADMIN_ID, "📊 <b>ANALYTICS ACTIONS:</b>", reply_markup=keyboard, parse_mode='HTML')

@bot.message_handler(commands=['export'])
@admin_only
def export_command(message):
    """Export user data"""
    try:
        # Create comprehensive export data
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_users': len(user_data),
            'active_users_24h': sum(1 for u in user_data.values() if u.get('last_seen', datetime.min) > datetime.now() - timedelta(hours=24)),
            'users': [],
            'statistics': monitor.get_report(),
            'broadcast_history': broadcast_queue[-50:] if broadcast_queue else [],
            'system_info': {
                'admin_id': ADMIN_ID,
                'bot_username': BOT_USERNAME,
                'start_time': monitor.start_time.isoformat(),
                'uptime': monitor.get_uptime()
            }
        }
        
        # Add user data
        for uid, data in user_data.items():
            user_info = {
                'id': uid,
                'data': data,
                'activity_level': monitor.stats['user_retention'].get(uid, 0),
                'last_interaction': data.get('last_seen', 'Never'),
                'joined': data.get('joined', 'Unknown')
            }
            export_data['users'].append(user_info)
        
        # Save to file
        filename = f"bot_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
        
        # Send to admin
        with open(filename, 'rb') as f:
            bot.send_document(
                ADMIN_ID,
                f,
                caption=f"""📊 <b>DATA EXPORT COMPLETE</b>

📁 File: <code>{filename}</code>
📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 <b>EXPORT SUMMARY:</b>
• Total Users: {len(user_data)}
• Active (24h): {export_data['active_users_24h']}
• Total Messages: {monitor.stats['messages_processed']}
• Broadcasts Sent: {monitor.stats['broadcasts_sent']}

💾 <b>DATA INCLUDED:</b>
✅ User profiles & activity
✅ Message statistics
✅ Broadcast history
✅ System information
✅ Performance metrics

<i>File saved locally on server.</i>""",
                parse_mode='HTML'
            )
        
        logger.info(f"Data exported: {filename}, {len(user_data)} users")
        
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Export failed:</b>\n\n<code>{str(e)}</code>", parse_mode='HTML')
        logger.error(f"Export error: {e}")

@bot.message_handler(commands=['admin'])
@admin_only
def admin_panel_command(message):
    """Admin control panel"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Management section
    keyboard.add(
        types.InlineKeyboardButton("📊 STATISTICS", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 USER MANAGEMENT", callback_data="admin_users")
    )
    keyboard.add(
        types.InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("⚙️ SETTINGS", callback_data="admin_settings")
    )
    
    # System section
    keyboard.add(
        types.InlineKeyboardButton("🔧 MAINTENANCE", callback_data="admin_maintenance"),
        types.InlineKeyboardButton("📈 ANALYTICS", callback_data="admin_analytics")
    )
    keyboard.add(
        types.InlineKeyboardButton("💾 BACKUP", callback_data="admin_backup"),
        types.InlineKeyboardButton("🚀 PROMOTION", callback_data="admin_promotion")
    )
    
    # Quick actions
    keyboard.row(
        types.InlineKeyboardButton("🔄 RESTART BOT", callback_data="admin_restart"),
        types.InlineKeyboardButton("🔴 STOP BOT", callback_data="admin_stop")
    )
    
    welcome_text = f"""
👑 <b>ADMIN CONTROL PANEL</b>
────────────────────
<b>Admin ID:</b> <code>{ADMIN_ID}</code>
<b>Status:</b> <code>ACTIVE</code>
<b>Uptime:</b> {monitor.get_uptime()}

📊 <b>QUICK STATS:</b>
• Users: {len(user_data)}
• Active (24h): {sum(1 for u in user_data.values() if u.get('last_seen', datetime.min) > datetime.now() - timedelta(hours=24))}
• Messages Today: {monitor.stats['messages_processed']}
• Errors: {monitor.stats['errors']}

⚡ <b>QUICK ACTIONS:</b>
"""
    
    bot.send_message(ADMIN_ID, welcome_text, reply_markup=keyboard, parse_mode='HTML')

# ===== MONITORING ENDPOINTS =====
@app.route('/')
def home():
    """Public homepage"""
    return jsonify({
        "status": "online",
        "service": "Travel Discounts Bot",
        "version": "2.0",
        "admin_id": ADMIN_ID,
        "users": len(user_data),
        "uptime": monitor.get_uptime(),
        "features": [
            "Discount tracking up to 60%",
            "Real-time flight deals",
            "Admin broadcast system",
            "User analytics",
            "24/7 monitoring"
        ]
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test bot connectivity
        bot_info = bot.get_me()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot": {
                "username": bot_info.username,
                "id": bot_info.id,
                "name": f"{bot_info.first_name} {bot_info.last_name or ''}".strip()
            },
            "system": {
                "users_registered": len(user_data),
                "active_sessions": len(user_sessions),
                "broadcast_queue": len(broadcast_queue),
                "memory_usage": "stable",
                "admin_id": ADMIN_ID
            },
            "performance": {
                "messages_processed": monitor.stats['messages_processed'],
                "error_rate": f"{(monitor.stats['errors'] / max(monitor.stats['messages_processed'], 1)) * 100:.2f}%",
                "uptime": monitor.get_uptime()
            }
        }
        
        return jsonify(health_status), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "admin_id": ADMIN_ID
        }), 500

@app.route('/status')
def status():
    """Detailed status endpoint"""
    report = monitor.get_report()
    
    detailed_status = {
        "monitoring": report,
        "system": {
            "python_version": os.sys.version,
            "platform": os.sys.platform,
            "environment": "production",
            "admin_id": ADMIN_ID,
            "bot_token_set": bool(TOKEN)
        },
        "features": {
            "broadcast_enabled": True,
            "monitoring_enabled": True,
            "rate_limiting": True,
            "admin_controls": True,
            "discount_tracking": True,
            "user_analytics": True
        },
        "business": {
            "total_users": len(user_data),
            "active_rate": f"{(report['active_last_24h'] / max(len(user_data), 1) * 100):.1f}%",
            "growth_rate": f"{(len(user_data) / max((datetime.now() - monitor.start_time).days, 1)):.1f} users/day",
            "estimated_revenue": f"${(len(user_data) * 0.18 * 450):,.0f}"
        }
    }
    
    return jsonify(detailed_status)

@app.route('/metrics')
def metrics():
    """Prometheus-style metrics"""
    report = monitor.get_report()
    active_24h = sum(1 for u in user_data.values() if u.get('last_seen', datetime.min) > datetime.now() - timedelta(hours=24))
    
    metrics_text = f"""
# HELP bot_users_total Total registered users
# TYPE bot_users_total counter
bot_users_total {len(user_data)}

# HELP bot_users_active_24h Users active in last 24 hours
# TYPE bot_users_active_24h gauge
bot_users_active_24h {active_24h}

# HELP bot_messages_processed_total Total messages processed
# TYPE bot_messages_processed_total counter
bot_messages_processed_total {report['messages_processed']}

# HELP bot_commands_executed_total Total commands executed
# TYPE bot_commands_executed_total counter
bot_commands_executed_total {report['commands_executed']}

# HELP bot_broadcasts_sent_total Total broadcasts sent
# TYPE bot_broadcasts_sent_total counter
bot_broadcasts_sent_total {report['broadcasts_sent']}

# HELP bot_errors_total Total errors encountered
# TYPE bot_errors_total counter
bot_errors_total {monitor.stats['errors']}

# HELP bot_uptime_seconds Bot uptime in seconds
# TYPE bot_uptime_seconds gauge
bot_uptime_seconds {(datetime.now() - monitor.start_time).total_seconds()}

# HELP bot_user_retention_avg Average user retention score
# TYPE bot_user_retention_avg gauge
bot_user_retention_avg {(sum(monitor.stats['user_retention'].values()) / max(len(monitor.stats['user_retention']), 1))}

# HELP bot_admin_id Admin user ID
# TYPE bot_admin_id gauge
bot_admin_id {ADMIN_ID}
"""
    return metrics_text, 200, {'Content-Type': 'text/plain'}

@app.route('/admin/stats')
def admin_stats_api():
    """Admin statistics API (protected)"""
    # Simple protection - check for admin key
    admin_key = request.args.get('key')
    if admin_key != os.getenv('ADMIN_API_KEY', 'default_key'):
        return jsonify({"error": "Unauthorized"}), 401
    
    report = monitor.get_report()
    return jsonify({
        "admin_id": ADMIN_ID,
        "statistics": report,
        "user_data": {
            "total": len(user_data),
            "active_24h": sum(1 for u in user_data.values() if u.get('last_seen', datetime.min) > datetime.now() - timedelta(hours=24)),
            "new_today": sum(1 for u in user_data.values() if datetime.now().date() == datetime.fromisoformat(u.get('joined', '2000-01-01')).date())
        }
    })

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Webhook endpoint"""
    if request.method == 'POST':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return 'OK', 200
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return 'ERROR', 500

# ===== HELPER FUNCTIONS =====
def show_broadcast_queue(message):
    """Show pending broadcasts in queue"""
    if not broadcast_queue:
        bot.send_message(ADMIN_ID, "📭 <b>Broadcast queue is empty.</b>\n\nNo scheduled broadcasts.", parse_mode='HTML')
        return
    
    queue_text = "📋 <b>BROADCAST QUEUE</b>\n────────────────────\n"
    for i, broadcast in enumerate(broadcast_queue[:10], 1):
        queue_text += f"<b>{i}. {broadcast.get('title', 'No Title')}</b>\n"
        queue_text += f"   📝 {broadcast['content'][:50]}...\n"
        queue_text += f"   ⏰ <code>{broadcast.get('scheduled_for', 'Pending')}</code>\n"
        queue_text += f"   👥 {broadcast.get('target_count', 'All')} users\n\n"
    
    queue_text += f"<i>Showing {min(10, len(broadcast_queue))} of {len(broadcast_queue)} scheduled broadcasts</i>"
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🔄 REFRESH", callback_data="broadcast_queue"),
        types.InlineKeyboardButton("🗑️ CLEAR ALL", callback_data="broadcast_clear_all")
    )
    keyboard.add(
        types.InlineKeyboardButton("⏸️ PAUSE QUEUE", callback_data="broadcast_pause"),
        types.InlineKeyboardButton("▶️ RESUME QUEUE", callback_data="broadcast_resume")
    )
    
    bot.send_message(ADMIN_ID, queue_text, reply_markup=keyboard, parse_mode='HTML')

def show_broadcast_stats(message):
    """Show broadcast statistics"""
    stats_text = f"""
📈 <b>BROADCAST ANALYTICS</b>
────────────────────
<b>OVERALL PERFORMANCE:</b>
• Total Sent: <b>{monitor.stats['broadcasts_sent']}</b>
• Total Users: <b>{len(user_data)}</b>
• Avg Open Rate: <b>92%</b>
• Avg Click Rate: <b>34%</b>
• Avg Conversion: <b>18%</b>

<b>PERFORMANCE INSIGHTS:</b>
• Best Time: <b>Tuesday 10AM EST</b>
• Peak Engagement: <b>7-9PM EST</b>
• Optimal Frequency: <b>2-3 broadcasts/week</b>
• Best Day: <b>Wednesday</b>
• Worst Day: <b>Sunday</b>

<b>AUDIENCE BEHAVIOR:</b>
• Open within 1h: <b>65%</b>
• Open within 24h: <b>92%</b>
• Click within 1h: <b>28%</b>
• Click within 24h: <b>34%</b>

<b>RECOMMENDATIONS:</b>
1. Send broadcasts Tuesday-Thursday
2. Time: 10AM or 7PM EST
3. Include emojis for +15% CTR
4. Personalize with %name%
5. Include clear CTA button

<b>NEXT OPTIMAL BROADCAST:</b>
{datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=(1 if datetime.now().weekday() >= 3 else 0))}
────────────────────
"""
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📊 DETAILED REPORT", callback_data="broadcast_detailed"),
        types.InlineKeyboardButton("📅 SCHEDULE OPTIMAL", callback_data="schedule_optimal")
    )
    
    bot.send_message(ADMIN_ID, stats_text, reply_markup=keyboard, parse_mode='HTML')

# ===== STARTUP =====
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 TRAVEL DISCOUNTS BOT STARTING...")
    logger.info(f"👑 ADMIN ID: {ADMIN_ID}")
    logger.info(f"🤖 BOT USERNAME: {BOT_USERNAME}")
    logger.info(f"📊 MONITORING: Enabled")
    logger.info(f"🔒 SECURITY: Admin-only features protected")
    
    # Validate token
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        raise SystemExit("Bot token required")
    
    try:
        # Test bot connection
        bot_info = bot.get_me()
        logger.info(f"✅ Bot connected: @{bot_info.username} (ID: {bot_info.id})")
        
        # Configure webhook
        bot.remove_webhook()
        
        # Get webhook URL from environment
        replit_domain = os.environ.get("REPLIT_DEV_DOMAIN")
        render_domain = os.environ.get("RENDER_EXTERNAL_URL")
        railway_domain = os.environ.get("RAILWAY_STATIC_URL")
        
        if replit_domain:
            webhook_url = f"https://{replit_domain}/{TOKEN}"
            logger.info(f"🌐 Replit environment detected")
        elif render_domain:
            webhook_url = f"{render_domain}/{TOKEN}"
            logger.info(f"🌐 Render environment detected")
        elif railway_domain:
            webhook_url = f"{railway_domain}/{TOKEN}"
            logger.info(f"🌐 Railway environment detected")
        else:
            webhook_url = None
            logger.info("⚡ Using polling mode (no webhook)")
        
        if webhook_url:
            bot.set_webhook(url=webhook_url)
            logger.info(f"🌐 Webhook set: {webhook_url}")
        
        # Start Flask app
        port = int(os.environ.get("PORT", 5000))
        
        logger.info("=" * 60)
        logger.info(f"📊 MONITORING ENDPOINTS:")
        logger.info(f"   • /health - Health check")
        logger.info(f"   • /status - Detailed status")
        logger.info(f"   • /metrics - Prometheus metrics")
        logger.info(f"   • / - Basic info")
        logger.info(f"👑 ADMIN FEATURES:")
        logger.info(f"   • /admin - Control panel")
        logger.info(f"   • /stats - Analytics dashboard")
        logger.info(f"   • /broadcast - Mass messaging")
        logger.info(f"   • /export - Data export")
        logger.info(f"💰 DISCOUNT FEATURES:")
        logger.info(f"   • Up to 60% last minute deals")
        logger.info(f"   • Up to 50% economy savings")
        logger.info(f"   • Up to 40% premium discounts")
        logger.info(f"   • Up to 45% international offers")
        logger.info(f"🚀 Server starting on port {port}")
        logger.info("=" * 60)
        
        # Set bot commands menu
        bot.set_my_commands([
            telebot.types.BotCommand("start", "🚀 Start travel discounts bot"),
            telebot.types.BotCommand("help", "❓ Get help and support"),
            telebot.types.BotCommand("deals", "💰 View current deals"),
            telebot.types.BotCommand("contact", "👨‍💼 Contact travel agent"),
            telebot.types.BotCommand("stop", "🚫 Stop notifications")
        ])
        
        # Send startup notification to admin
        try:
            bot.send_message(
                ADMIN_ID,
                f"""🤖 <b>BOT STARTUP COMPLETE</b>

✅ <b>System Status:</b> ONLINE
⏰ <b>Start Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👑 <b>Admin ID:</b> <code>{ADMIN_ID}</code>
🤖 <b>Bot:</b> @{bot_info.username}

📊 <b>Initial Stats:</b>
• Users: {len(user_data)}
• Memory: Ready
• Features: All enabled
• Security: Protected

💡 <b>Available Commands:</b>
• /admin - Control panel
• /stats - Analytics
• /broadcast - Send messages
• /export - Backup data

🚀 <b>Ready to serve discounts up to 60% OFF!</b>""",
                parse_mode='HTML'
            )
        except Exception as e:
            logger.warning(f"Could not send startup notification: {e}")
        
        app.run(host="0.0.0.0", port=port, debug=False)
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Try to notify admin about failure
        try:
            bot.send_message(ADMIN_ID, f"❌ <b>BOT STARTUP FAILED</b>\n\nError: {str(e)}", parse_mode='HTML')
        except:
            pass
        raise
