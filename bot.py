import os
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests

TOKEN = os.getenv("TOKEN")
REMOVE_BG = os.getenv("REMOVE_BG", "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "صديقي"
    keyboard = [
        [InlineKeyboardButton("🧹 حذف الخلفية", callback_data="remove_bg")],
        [InlineKeyboardButton("🧷 تحويل الصورة إلى ملصق", callback_data="sticker")],
        [InlineKeyboardButton("↩️ الرجوع للرئيسية", callback_data="home")]
    ]
    await update.message.reply_text(
        f"اهلاً {name} 👋\nاختار الخدمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "home":
        await start(query, context)

    elif query.data == "remove_bg":
        await query.edit_message_text("ارسل صورة الآن وسأحذف الخلفية ✂️")

    elif query.data == "sticker":
        await query.edit_message_text("ارسل صورة الآن وسأحولها إلى ملصق 🧷")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    file = await update.message.photo[-1].get_file()
    photo = await file.download_as_bytearray()

    text = (update.message.reply_to_message.text if update.message.reply_to_message else "")

    # حذف الخلفية
    if "حذف الخلفية" in text or "✂️" in text:
        if not REMOVE_BG:
            await update.message.reply_text("⚠️ لا يوجد REMOVE_BG KEY")
            return

        res = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": photo},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG},
        )

        if res.status_code == 200:
            await update.message.reply_photo(res.content, caption="تم حذف الخلفية ✅")
        else:
            await update.message.reply_text("فشل حذف الخلفية ❌")

    # ملصق
    else:
        await update.message.reply_sticker(photo)
        await update.message.reply_text("تم تحويلها إلى ملصق ✅")

# ====== WEB SERVER KEEP ALIVE ======
async def web_handler(request):
    return web.Response(text="Bot Running OK")

async def run_web():
    app = web.Application()
    app.router.add_get("/", web_handler)
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    await app.initialize()
    await app.start()
    await app.run_polling()

async def main():
    await asyncio.gather(run_web(), run_bot())

asyncio.run(main())
