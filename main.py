import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import requests
from io import BytesIO
from flask import Flask, request
from telegram import Bot

API_TOKEN = os.getenv('API_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # URL webhook của bạn
LOGO_PATH = 'logo.png'

app_flask = Flask(__name__)

# Hàm chèn logo vào ảnh
def add_logo(image: Image, logo: Image) -> Image:
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    logo = logo.resize((image.width, int((logo.height / logo.width) * image.width)), Image.LANCZOS)

    base_width, base_height = image.size
    logo_width, logo_height = logo.size
    position = ((base_width - logo_width) // 2, (base_height - logo_height) // 2)

    image.paste(logo, position, logo)
    return image

# Hàm xử lý khi bot nhận được tệp ảnh
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = await context.bot.get_file(update.message.document.file_id)
    file_data = requests.get(file.file_path).content

    image = Image.open(BytesIO(file_data))
    logo = Image.open(LOGO_PATH)

    processed_image = add_logo(image, logo)

    output = BytesIO()
    processed_image.save(output, format='PNG')
    output.seek(0)

    await update.message.reply_document(document=output, filename='processed_image.png')

# Hàm xử lý khi bot nhận được ảnh
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = await context.bot.get_file(update.message.photo[-1].file_id)
    file_data = requests.get(file.file_path).content

    image = Image.open(BytesIO(file_data))
    logo = Image.open(LOGO_PATH)

    processed_image = add_logo(image, logo)

    output = BytesIO()
    processed_image.save(output, format='PNG')
    output.seek(0)

    await update.message.reply_document(document=output, filename='processed_image.png')

# Hàm xử lý lệnh hello
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}! Hãy gửi cho tôi một bức ảnh hoặc một tệp ảnh để tôi chèn logo vào.')

# Thiết lập webhook
async def setup_webhook(bot: Bot):
    await bot.set_webhook(url=f'{WEBHOOK_URL}/{API_TOKEN}')

# Khởi tạo và chạy bot
application = ApplicationBuilder().token(API_TOKEN).build()

application.add_handler(CommandHandler("hello", hello))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

@app_flask.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.update_queue.put(update)
    return "OK", 200

if __name__ == '__main__':
    bot = Bot(token=API_TOKEN)
    
    # Chạy setup_webhook trong một vòng lặp sự kiện
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_webhook(bot))
    
    app_flask.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
