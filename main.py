import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pytrends.request import TrendReq

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ بوت الترند العربي جاهز 🇸🇦🔥")

async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ اكتب كود الدولة مثل:\n/trend sa\n/trend eg\n/trend kw")
        return
    
    country = context.args[0].lower()
    pytrends = TrendReq(hl='ar', tz=3)

    try:
        pytrends.build_payload(kw_list=['news'], geo=country.upper())
        trending = pytrends.trending_searches(pn=country)

        if trending.empty:
            await update.message.reply_text("❌ كود الدولة غير صحيح أو Google رفض الطلب")
            return
        
        results = "\n".join([f"🔹 {t[0]}" for t in trending.head(10).values])
        await update.message.reply_text(f"🔥 أعلى ترند في {country.upper()}:\n\n{results}")

    except Exception as e:
        await update.message.reply_text("❌ كود الدولة غير صحيح أو Google رفض الطلب")

async def on_startup(app):
    await app.bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trend", trend))

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
