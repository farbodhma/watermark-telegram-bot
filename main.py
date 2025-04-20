import os
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "PUT-YOUR-TOKEN-HERE")
WATERMARK_PATH = "watermark.png"

app = FastAPI()
bot_app = Application.builder().token(TELEGRAM_TOKEN).build()

def add_watermark(image: Image.Image, watermark: Image.Image, scale=0.4) -> Image.Image:
    new_width = int(image.width * scale)
    new_height = int(watermark.height * (new_width / watermark.width))
    watermark_resized = watermark.resize((new_width, new_height), Image.LANCZOS)

    x = (image.width - watermark_resized.width) // 2
    y = (image.height - watermark_resized.height) // 2

    image.paste(watermark_resized, (x, y), watermark_resized)
    return image

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    file_bytes = BytesIO()
    await photo_file.download(out=file_bytes)
    file_bytes.seek(0)

    base_image = Image.open(file_bytes).convert("RGBA")
    watermark = Image.open(WATERMARK_PATH).convert("RGBA")
    result = add_watermark(base_image, watermark)

    output = BytesIO()
    result.convert("RGB").save(output, format="JPEG")
    output.seek(0)

    await update.message.reply_photo(photo=output)

bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}
