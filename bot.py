import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from rembg import remove
from PIL import Image
import io

TOKEN = "8297837826:AAHj6l32pQFrxduUTEAsAPzDr09_9mBDILc"
PORT = 10000  # Render uses this

# ====== Handlers ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"اهلاً يا {user.first_name} 👋\nالبوت شغال 24 ساعة 🔥")

async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        img_bytes = await file.download_as_bytearray()
        output = remove(img_bytes)
        await update.message.reply_photo(photo=output)
    else:
        await update.message.reply_text("ارسل صورة لحذف الخلفية")

async def to_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        img_bytes = await file.download_as_bytearray()
        image = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        with io.BytesIO() as output:
            image.save(output, format="WEBP")
            output.seek(0)
            await update.message.reply_sticker(sticker=output)
    else:
        await update.message.reply_text("ارسل صورة لتحويلها لملصق")

# ====== Web Server ======
async def handle(request):
    return web.Response(text="Bot is Running ✔️")

async def run_web():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌍 Web Server Running on port {PORT}")

# ====== Bot Runner ======
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO & filters.Caption("/remove_bg"), remove_bg))
    app.add_handler(MessageHandler(filters.PHOTO & filters.Caption("/sticker"), to_sticker))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("🤖 Bot Running...")

    await asyncio.Event().wait()   # keep bot alive

# ====== MAIN ======
async def main():
    await asyncio.gather(run_web(), run_bot())

if __name__ == "__main__":
    asyncio.run(main())
