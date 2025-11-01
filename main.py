import os
from telegram.ext import ApplicationBuilder, CommandHandler
from pytrends.request import TrendReq

TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("✅ بوت الترند العربي جاهز")

async def trend(update, context):
    # كود الدولة (افتراضي SA)
    country = "SA"
    if context.args:
        country = context.args[0].upper()

    # ربط pytrends
    pytrends = TrendReq(hl='ar', tz=360)
    try:
        trending = pytrends.trending_searches(pn=country)
    except:
        await update.message.reply_text("❌ كود الدولة غير صحيح أو Google رفض الطلب")
        return
    
    trends_list = trending[0].tolist()[:10]  # أول 10 ترندات
    response = f"🔥 ترندات {country} الآن:\n\n"
    for i, t in enumerate(trends_list, start=1):
        response += f"{i}️⃣ {t}\n"

    await update.message.reply_text(response)

async def on_startup(app):
    await app.bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trend", trend))
    app.run_polling()
