import datetime
import json
import os
from telegram import Bot, Update, ChatMemberUpdated
from telegram.ext import (
    ApplicationBuilder, ContextTypes, ChatMemberHandler
)
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Armenia timezone
ARMENIA_TZ = pytz.timezone("Asia/Yerevan")

# ---- Birthday Database ----
birthdays = {
    "Davit": {
        "date": "11-25",
        "message": "🐍 ՇՆՈՐՀԱՎՈՐ ՏՈՆԴ, ԿտրիՃ ԴԱՎԻ՛Թ! Python-ի վարպետ, Շների Թագավոր, Սոնայի սրտի տիրակալ, մեր սրտի կատակերգու ու Լոլիկով Ձվածեղի Գորդոն Ռամզի։
                    Դու այն եզակի «մարդ–հումորային օբյեկտն» ես, որ կարողանում է միացնել կոդինգը, թագավորական շնային խնամքն ու Matthew McConaughey–ի աստիճանի դերասանական խաղը։
                    Միչիգանն ու Ջինան ապրում են այնպիսի շքեղությամբ, որ մենք արդեն համոզված ենք՝ շուտով իրենք քեզ «սիրելի ծառա» են կոչելու—ամենալավ սնունդ, ամենալավ խնամք, ամեն օր զբոսանք…
                    Դու ճկուն ես մինչև 3D անիմացիայի սահման,
                     Ու քո հումորը էնքան դիպուկ է, որ Python-ը Error չի տալիս քեզ վրա՝ զուտ ամաչելով։
                    Պարգևի հետ ձեր մանկության քոլաբորացիան Oscar-ի արժանի է, իսկ Վաչեն ու Դավոն միշտ այնտեղ՝ կսպասեն ու կլրացնեն այն՝ կալյանային փիլիսոփայական նիստերի ներքո։
                    Սոնան՝ քո թագուհին 👸💕
                     Դու նրան այնպիսի ջերմությամբ ու սիրով ես վերաբերվում, որ Hollywood-ի ռոմկոմները լացում են անկյունում ու ասում՝ «էս ոնց ա անում էս Դավոն»։
                    Շարունակիր խորանալ աշխարհի ամենահետաքրքիր թեմաների մեջ՝ սկսած տիեզերքից մինչև ոնց համով սարքել լոլիկով ձվածեղ:
                    Դավիթ ջան, թող էս տարին լի լինի էն նույն լեգենդար տրամադրությամբ, ինչ nonstop բերում ես՝ առանց կրկնվելու, առանց Error-ի, առանց Buffer Overflow-ի։ Կյանքդ լինի այնքան կատարյալ որքան դու ես տալիս Միչիգանին ու Ջինային, Սոնայի հետ լինեք ավելի երջանիկ, աճեք, բազմանաք, դե լոլիկով ձվածեղդ  էլ Michelin star-ի արժանանա …",
        "sticker": "CAACAgQAAx..."
    },
    "Bob": {
        "date": "12-01",
        "message": "🎉 Happy Birthday Bob! 🎈",
        "sticker": "CAACAgIAAx..."
    }
}

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
                await context.bot.send_message(chat_id, "👋 Hello MM members! Starting from now I’ll send birthday messages here! Take a breath, relax and enjoy it. :D")
        # Bot removed
        elif new_status == "left":
            groups = load_groups()
            if chat_id in groups:
                groups.remove(chat_id)
                save_groups(groups)


# ------------------ BIRTHDAY CHECK -----------------
async def check_birthdays(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now(ARMENIA_TZ).strftime("%m-%d")
    groups = load_groups()

    for name, data in birthdays.items():
        if data["date"] == today:
            for group_id in groups:
                await context.bot.send_message(group_id, f"{data['message']} 🎉")
                await context.bot.send_sticker(group_id, data["sticker"])


# ------------------ MAIN ---------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Detect when bot is added / removed
    app.add_handler(ChatMemberHandler(bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

    # Schedule daily birthday check at 8:00 AM Armenia time
    job_queue = app.job_queue
    if job_queue:
        time_obj = datetime.time(hour=11, minute=11, tzinfo=ARMENIA_TZ)
        job_queue.run_daily(check_birthdays, time=time_obj)

    app.run_polling()


if __name__ == "__main__":
    main()
