from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import requests
import os
from io import BytesIO

API_TOKEN = os.getenv('API_TOKEN')

# Đường dẫn đến logo
LOGO_PATH = 'logo.png'

def add_logo(image: Image, logo: Image) -> Image:
    # Đảm bảo logo có kênh alpha
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    # Thay đổi kích thước logo
    logo = logo.resize((image.width, int((logo.height / logo.width) * image.width)), Image.LANCZOS)

    # Tính vị trí để chèn logo
    base_width, base_height = image.size
    logo_width, logo_height = logo.size
    position = ((base_width - logo_width) // 2, (base_height - logo_height) // 2)

    # Chèn logo vào ảnh
    image.paste(logo, position, logo)  # Sử dụng logo làm mặt nạ
    return image

# Hàm xử lý khi bot nhận được tệp ảnh
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Tải ảnh từ tệp tin đính kèm
    file = await context.bot.get_file(update.message.document.file_id)
    file_data = requests.get(file.file_path).content

    # Mở ảnh vừa tải
    image = Image.open(BytesIO(file_data))
    logo = Image.open(LOGO_PATH)

    # Chèn logo vào ảnh
    processed_image = add_logo(image, logo)

    # Lưu ảnh đã chèn logo vào bộ nhớ tạm
    output = BytesIO()
    processed_image.save(output, format='PNG')
    output.seek(0)

    # Gửi lại ảnh đã chèn logo dưới dạng tệp
    await update.message.reply_document(document=output, filename='processed_image.png')

# Hàm xử lý khi bot nhận được ảnh
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Tải ảnh từ tin nhắn
    file = await context.bot.get_file(update.message.photo[-1].file_id)
    file_data = requests.get(file.file_path).content

    # Mở ảnh vừa tải
    image = Image.open(BytesIO(file_data))
    logo = Image.open(LOGO_PATH)

    # Chèn logo vào ảnh
    processed_image = add_logo(image, logo)

    # Lưu ảnh đã chèn logo vào bộ nhớ tạm
    output = BytesIO()
    processed_image.save(output, format='PNG')
    output.seek(0)

    # Gửi lại ảnh đã chèn logo cho người dùng dưới dạng tệp để giữ chất lượng
    await update.message.reply_document(document=output, filename='processed_image.png')

# Hàm xử lý lệnh hello
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}! Hãy gửi cho tôi một bức ảnh hoặc một tệp ảnh để tôi chèn logo vào.')

# Khởi tạo và chạy bot
app = ApplicationBuilder().token(API_TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

# Chạy bot
app.run_polling()
