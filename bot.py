import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 10000))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(f"مرحبًا يا {name} 👋\nالبوت شغال تمام ❤️")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 البوت شغال 24 ساعة إن شاء الله")


async def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, echo))

    # تشغيل البوت يدويًا بدون run_polling
    await app.initialize()
    await app.start()
    print("🤖 Bot Started...")

    # نمنعه من الإغلاق
    await asyncio.Event().wait()


async def run_web():
    async def home(request):
        return web.Response(text="Bot is Running ✔️")

    app = web.Application()
    app.router.add_get("/", home)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌍 Web Server Running on port {PORT}")


async def main():
    await asyncio.gather(run_bot(), run_web())


if __name__ == "__main__":
    asyncio.run(main())
