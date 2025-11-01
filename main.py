import os
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("بوت الترند العربي جاهز ✅")

async def on_startup(app):
    await app.bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling(on_startup=on_startup)
