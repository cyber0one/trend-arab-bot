import os
import logging
from typing import List

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from pytrends.request import TrendReq

# ============== ضبط السجل ==============
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("arab-trend-bot")

# ============== إعدادات عامة ==============
BOT_TOKEN = os.getenv("BOT_TOKEN")  # لا تغيّر اسم المتغير في Render
if not BOT_TOKEN:
    raise RuntimeError("Environment variable BOT_TOKEN is missing.")

# pytrends: واجهة عربية وتوقيت الرياض (UTC+3 دقائق = 180)
def make_pytrends() -> TrendReq:
    return TrendReq(hl="ar-SA", tz=180)

# خريطة لأسماء الدول المطلوبة من pytrends.trending_searches (ليست ISO دائمًا)
PN_MAP = {
    "SA": "saudi_arabia",
    "EG": "egypt",
    "KW": "kuwait",
    "AE": "united_arab_emirates",
    "QA": "qatar",
    "BH": "bahrain",
    "OM": "oman",
    "US": "united_states",
    "GB": "united_kingdom",
    "DE": "germany",
    "FR": "france",
    "IT": "italy",
    "ES": "spain",
    "TR": "turkey",
    "IN": "india",
    "JP": "japan",
}

# ============== أوامر البوت ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("✅ بوت الترند العربي جاهز. جرب: /trend SA")

def normalize_cc(args: List[str]) -> str:
    if not args:
        return "SA"
    code = args[0].strip().upper()
    if len(code) != 2 or not code.isalpha():
        # إن دخل المستخدم شيء غير حرفين
        return "SA"
    return code

async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        cc = normalize_cc(context.args)
        pytrends = make_pytrends()

        # نحاول أولاً عبر trending_searches التي تحتاج أسماء خاصة من الخريطة
        queries = []
        pn = PN_MAP.get(cc)
        if pn:
            try:
                df = pytrends.trending_searches(pn=pn)
                queries = df[0].tolist() if not df.empty else []
            except Exception as e:
                logger.warning("trending_searches failed for %s (%s): %s", cc, pn, e)

        # لو فشلت أو ما فيه خريطة، نحاول today_searches برمز الدولة مباشرة (بعض الدول تعمل)
        if not queries:
            try:
                df2 = pytrends.today_searches(pn=cc)
                queries = df2.tolist() if df2 is not None else []
            except Exception as e:
                logger.warning("today_searches failed for %s: %s", cc, e)

        if not queries:
            await update.message.reply_text(
                f"⚠️ ما قدرت أجيب ترند لـ {cc}. جرّب رموز: SA, EG, KW, AE, QA, US, GB."
            )
            return

        top = queries[:10]
        lines = "\n".join(f"• {q}" for q in top)
        await update.message.reply_text(f"🌍 ترند {cc} (أعلى 10):\n{lines}")

    except Exception as e:
        logger.exception("trend handler exception: %s", e)
        await update.message.reply_text("❌ حصل خطأ أثناء جلب الترند. حاول لاحقًا.")

# ============== حذف الويبهوك قبل الـpolling ==============
async def on_startup(app):
    # مهم جداً لمنع Conflict إذا كان ويبهوك قديم مفعّل
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted. Starting clean polling.")
    except Exception as e:
        logger.warning("Failed to delete webhook: %s", e)

# ============== نقطة التشغيل ==============
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trend", trend))

    # تشغيل واحد فقط
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
