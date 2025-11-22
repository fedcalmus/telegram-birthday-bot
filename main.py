import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot, Update, ChatMemberUpdated
from telegram.ext import (
    ApplicationBuilder, ContextTypes, ChatMemberHandler
)
import pytz

TOKEN = "8238756652:AAERvMbBXCOnc6Oqu8J3Xy-81bSO4hiekDs"

# Armenia timezone
ARMENIA_TZ = pytz.timezone("Asia/Yerevan")

# ---- Birthday Database ----
birthdays = {
    "Alice": {
        "date": "11-19",
        "message": "🎉 Happy Birthday Alice! 💐🎂",
        "sticker": "CAACAgQAAx..."
    },
    "Bob": {
        "date": "12-01",
        "message": "🎉 Happy Birthday Bob! 🎈",
        "sticker": "CAACAgIAAx..."
    }
}

bot = Bot(TOKEN)

GROUPS_FILE = "groups.json"


# ------------------ GROUP STORAGE ------------------
def load_groups():
    try:
        with open(GROUPS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_groups(groups):
    with open(GROUPS_FILE, "w") as f:
        json.dump(groups, f)


# ---------------- BOT ADDED TO GROUP ----------------
async def bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.my_chat_member:
        new_status = update.my_chat_member.new_chat_member.status
        chat_id = update.my_chat_member.chat.id

        # Bot added to a group
        if new_status in ["member", "administrator"]:
            groups = load_groups()
            if chat_id not in groups:
                groups.append(chat_id)
                save_groups(groups)
                await bot.send_message(chat_id, "👋 Hello! I will now send birthday messages here.")
        # Bot removed
        elif new_status == "left":
            groups = load_groups()
            if chat_id in groups:
                groups.remove(chat_id)
                save_groups(groups)


# ------------------ BIRTHDAY CHECK -----------------
def check_birthdays():
    today = datetime.datetime.now(ARMENIA_TZ).strftime("%m-%d")
    groups = load_groups()

    for name, data in birthdays.items():
        if data["date"] == today:
            for group_id in groups:
                bot.send_message(group_id, f"{data['message']} 🎉")
                bot.send_sticker(group_id, data["sticker"])


# ------------------ MAIN ---------------------------
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Detect when bot is added / removed
    app.add_handler(ChatMemberHandler(bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

    # Scheduler
    scheduler = BackgroundScheduler(timezone=ARMENIA_TZ)
    scheduler.add_job(check_birthdays, "cron", hour=8, minute=0)
    scheduler.start()

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
