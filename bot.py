import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "ضع_توكن_بوتك_هنا"
PORT = 10000  # Render uses this


# ====== Telegram Handlers ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"اهلاً يا {user.first_name} 👋\nالبوت شغال 24 ساعة 🔥")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال الحمد لله 😎")


# ====== Web Server (for Render keep alive) ======
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


# ====== Telegram Bot Runner ======
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, echo))

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
