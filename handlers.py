# job_alert_bot/handlers.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
import database as db

router = Router()

# --- Welcome and Help Messages ---
WELCOME_MESSAGE = """
👋 Welcome to the Job Alert Bot!

I will help you find remote jobs by scraping popular job boards daily.

**Available Commands:**
/subscribe <keyword> - Add a job filter (e.g., /subscribe Python)
/unsubscribe <keyword> - Remove a job filter
/list - Show your current subscriptions
/help - Display this help message

Start by subscribing to a keyword you're interested in!
"""

HELP_MESSAGE = """
**How to use the Job Alert Bot:**

1️⃣ **Subscribe to Keywords:**
   Use the `/subscribe` command followed by a keyword. You can add multiple keywords.
   *Example:* `/subscribe react`
   *Example:* `/subscribe data entry`

2️⃣ **List Your Subscriptions:**
   Use the `/list` command to see all the keywords you are currently subscribed to.

3️⃣ **Unsubscribe from Keywords:**
   Use the `/unsubscribe` command followed by the keyword you want to remove.
   *Example:* `/unsubscribe react`

The bot will automatically scan for new jobs once a day and send you a notification if a job title matches one of your keywords.
"""

# --- Command Handlers ---

@router.message(CommandStart())
async def handle_start(message: Message):
    """Handler for the /start command."""
    await message.answer(WELCOME_MESSAGE, parse_mode="Markdown")

@router.message(Command("help"))
async def handle_help(message: Message):
    """Handler for the /help command."""
    await message.answer(HELP_MESSAGE, parse_mode="Markdown")

@router.message(Command("subscribe"))
async def handle_subscribe(message: Message):
    """Handler for the /subscribe <keyword> command."""
    keyword = message.text.split(maxsplit=1)[1:]
    if not keyword:
        await message.answer("Please provide a keyword to subscribe. Usage: `/subscribe <keyword>`")
        return
    
    keyword = keyword[0]
    success = await db.add_subscription(message.from_user.id, keyword)
    if success:
        await message.answer(f"✅ You have successfully subscribed to job alerts for: **{keyword}**", parse_mode="Markdown")
    else:
        await message.answer(f"🤔 You are already subscribed to **{keyword}**.", parse_mode="Markdown")

@router.message(Command("unsubscribe"))
async def handle_unsubscribe(message: Message):
    """Handler for the /unsubscribe <keyword> command."""
    keyword = message.text.split(maxsplit=1)[1:]
    if not keyword:
        await message.answer("Please provide a keyword to unsubscribe. Usage: `/unsubscribe <keyword>`")
        return

    keyword = keyword[0]
    success = await db.remove_subscription(message.from_user.id, keyword)
    if success:
        await message.answer(f"🗑️ You have successfully unsubscribed from: **{keyword}**", parse_mode="Markdown")
    else:
        await message.answer(f"❌ You were not subscribed to **{keyword}**.", parse_mode="Markdown")

@router.message(Command("list"))
async def handle_list(message: Message):
    """Handler for the /list command."""
    subscriptions = await db.get_subscriptions(message.from_user.id)
    if not subscriptions:
        await message.answer("You are not subscribed to any keywords yet. Use `/subscribe <keyword>` to start.")
        return

    # Format the list for better readability
    sub_list = "\n".join([f"- `{sub}`" for sub in subscriptions])
    response_text = f"**Your current subscriptions:**\n{sub_list}"
    await message.answer(response_text, parse_mode="Markdown")