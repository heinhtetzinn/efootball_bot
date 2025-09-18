import os
# ---------- user tracking (add here) ----------
USERS_FILE = "users.txt"

def ensure_users_file():
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w", encoding="utf-8").close()

def save_user(user_id):
    """Save a user id to users.txt if not already present."""
    ensure_users_file()
    user_str = str(user_id)
    with open(USERS_FILE, "a+", encoding="utf-8") as f:
        f.seek(0)
        known = {line.strip() for line in f if line.strip()}
        if user_str not in known:
            f.write(user_str + "\n")

def count_users():
    """Return how many user ids are stored (non-empty lines)."""
    ensure_users_file()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())
# ----------------------------------------------

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Read your bot token from an environment variable or prompt for it
TOKEN = "8216941190:AAHXmp96N1okm4TtStj81Sl1kFr5iBEOOVw"

IMAGES_ROOT = "images"
TOPICS = {"konami_create": "konami_create",
          "watch_mail": "watch_mail",
          "forget_pass": "forget_pass",
          "coin": "coin"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    keyboard = [[InlineKeyboardButton("Konami Gmail ပြောင်းနည်း", callback_data="konami_create")],
                [InlineKeyboardButton("Konami ချိတ်ထားတဲ့ Mail ကြည့်နည်း", callback_data="watch_mail")],
                [InlineKeyboardButton("Password မေ့နေလျှင်", callback_data="forget_pass")],
                [InlineKeyboardButton("Coin ဝယ်ရန်", callback_data="coin")]]
    await update.message.reply_text("Choose a help topic:", reply_markup=InlineKeyboardMarkup(keyboard))

def list_images(folder):
    full = os.path.join(IMAGES_ROOT, folder)
    return [os.path.join(full, f) for f in sorted(os.listdir(full))
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]

async def send_album(chat_id, image_paths, context):
    for i in range(0, len(image_paths), 10):  # Telegram max 10 per album
        batch = image_paths[i:i+10]
        media = [InputMediaPhoto(open(p, "rb")) for p in batch]
        await context.bot.send_media_group(chat_id=chat_id, media=media)

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    save_user(query.from_user.id)
    await query.answer()
    imgs = list_images(TOPICS[query.data])
    if imgs:
        await send_album(query.message.chat.id, imgs, context)
    else:
        await query.message.reply_text("No images found for this topic.")

async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = count_users()
    await update.message.reply_text(f"Total users: {n}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", users_cmd))  # <--- our new line
    app.add_handler(CallbackQueryHandler(on_button))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
