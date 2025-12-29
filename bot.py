import os
from io import BytesIO
from PIL import Image
from rembg import remove
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from aiohttp import web

TOKEN = os.environ.get("BOT_TOKEN")  # ضع توكن بوتك في متغير BOT_TOKEN على Render

# رسالة ترحيبية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("حذف الخلفية", callback_data='remove_bg')],
        [InlineKeyboardButton("تحويل إلى ملصق", callback_data='to_sticker')],
        [InlineKeyboardButton("الرئيسية", callback_data='main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"أهلاً {username}! اختر ما تريد:", reply_markup=reply_markup)

# معالجة الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'main':
        await start(update, context)
        return

    if not context.user_data.get("last_photo"):
        await query.edit_message_text("أرسل صورة أولاً قبل اختيار هذا الخيار.")
        return

    photo_bytes = context.user_data["last_photo"]

    if query.data == 'remove_bg':
        output = remove(photo_bytes)
        await query.message.reply_photo(photo=output, caption="تم إزالة الخلفية!")
    elif query.data == 'to_sticker':
        img = Image.open(BytesIO(photo_bytes))
        bio = BytesIO()
        bio.name = 'sticker.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        await query.message.reply_sticker(sticker=bio)

# حفظ الصورة المرسلة
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = BytesIO()
    await photo_file.download(out=photo_bytes)
    context.user_data["last_photo"] = photo_bytes.getvalue()
    await update.message.reply_text("تم استلام الصورة! الآن اختر العملية من الأزرار.")

# إعداد Web Server بسيط لتجنب مشاكل Render
async def index(request):
    return web.Response(text="بوت Telegram شغال!")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    # تشغيل ويب سيرفر aiohttp
    runner = web.AppRunner(web.Application())
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

    print("🌍 Web Server Running on port", os.environ.get("PORT", 10000))
    print("🤖 Bot Started...")
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
