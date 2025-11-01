import os
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("بوت الترند العربي جاهز ✅")

async def post_init(app):
    # تأكد من إلغاء أي Webhook سابق وعدم استقبال رسائل قديمة
    await app.bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling(drop_pending_updates=True)
