import json, os, time
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8297171144:AAGbYGbwV-8NMijHTYH1sxe0h9YmJVCcz4I"
ADMIN_ID = 7878194733

DATA_FILE = "data.json"

# ---------- LOAD DATA ----------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {
        "users": {},       # user_id -> anon_id
        "blocked": [],     # anon_id
        "counter": 1000
    }

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if uid not in data["users"]:
        data["counter"] += 1
        data["users"][uid] = data["counter"]
        save()

    anon = data["users"][uid]

    await update.message.reply_text(
        f"🕶️ سلام به بات ناشناس عرفان خوش اومدی\n\n"
        f"👤 شناسه تو: ناشناس {anon}\n"
        f"🔐 هویتت کاملاً مخفیه\n"
        f"✉️ می‌تونی متن، عکس و ویس بفرستی"
    )

# ---------- USER SEND ----------
async def user_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    anon = data["users"].get(uid)

    if anon in data["blocked"]:
        return

    await context.bot.send_chat_action(chat_id=ADMIN_ID, action=ChatAction.TYPING)

    caption = update.message.caption or ""
    text = f"📩 از ناشناس {anon}\n\n{caption}"

    if update.message.text:
        await context.bot.send_message(ADMIN_ID, f"{text}\n{update.message.text}")
    elif update.message.voice:
        await context.bot.send_voice(ADMIN_ID, update.message.voice.file_id, caption=text)
    elif update.message.photo:
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption=text)

    await update.message.reply_text("✅ پیام ناشناس ارسال شد")

# ---------- ADMIN REPLY ----------
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        return

    try:
        anon = int([x for x in update.message.reply_to_message.text.split() if x.isdigit()][0])
    except:
        return

    user_id = None
    for uid, aid in data["users"].items():
        if aid == anon:
            user_id = int(uid)
            break

    if not user_id:
        return

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    time.sleep(1)

    if update.message.text:
        await context.bot.send_message(user_id, update.message.text)
    elif update.message.voice:
        await context.bot.send_voice(user_id, update.message.voice.file_id)
    elif update.message.photo:
        await context.bot.send_photo(user_id, update.message.photo[-1].file_id)

# ---------- ADMIN COMMANDS ----------
async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    anon = int(context.args[0])
    data["blocked"].append(anon)
    save()
    await update.message.reply_text(f"🚫 ناشناس {anon} بلاک شد")

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("block", block))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & filters.User(ADMIN_ID), admin_reply))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, user_send))

    print("🔥 GOD MODE Anonymous Bot running...")
    app.run_polling()

main()