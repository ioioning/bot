import logging
import os
from dotenv import load_dotenv

load_dotenv()
import ollama
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,

)

# 🔧 Налаштування логів
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 📋 Буфер останніх повідомлень
message_buffer = []

# 📌 Налаштування моделі Ollama
OLLAMA_MODEL = "llama3:8b"
MAX_BUFFER_MESSAGES = 20  # скільки повідомлень тримати в контексті


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я локальний модератор-бот на базі LLM ✊")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Збираємо історію
    message_buffer.append({"user": message.from_user.username, "text": message.text})
    if len(message_buffer) > MAX_BUFFER_MESSAGES:
        message_buffer.pop(0)

    # Відповідаємо лише якщо є згадка про бота
    if context.bot.username.lower() not in message.text.lower():
        return

    # Формуємо контекст
    context_text = "\n".join([f"@{m['user']}: {m['text']}" for m in message_buffer])
    prompt = (
        f"Ти є модератором Telegram-чату про австрійську школу економіки.\n"
        f"Твоя задача — підтримувати конструктивну дискусію, зупиняти флуд, тролінг і хамство.\n"
        f"Не соромся банити користувачів і називати їх по імені. Можеш бути суворим, іронічним, але завжди по суті.\n"
        f"Ось недавні повідомлення з чату:\n\n{context_text}\n\n"
        f"Відповідай як модератор."
    )

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        reply = response["message"]["content"].strip()
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Ollama error: {e}")
        await update.message.reply_text("⚠️ Виникла помилка при зверненні до моделі.")


def main():
    # 🔐 Замінити на свій Telegram токен
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущено з локальною LLM-моделлю через Ollama!")
    app.run_polling()


if __name__ == "__main__":
    main()

