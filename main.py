from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os # Add this line

WATERMARK_PATH = "watermark.png"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! عکس بفرستید تا با واترمارک برگردوندم."
    )

def add_watermark(image: Image.Image, watermark: Image.Image, scale=0.4) -> Image.Image:
    base = image.convert("RGBA")
    wm = watermark.convert("RGBA")

    # تغییر اندازه واترمارک
    new_w = int(base.width * scale)
    new_h = int(wm.height * (new_w / wm.width))
    wm_resized = wm.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # مرکز تصویر
    x = (base.width - new_w) // 2
    y = (base.height - new_h) // 2

    base.paste(wm_resized, (x, y), wm_resized)
    return base.convert("RGB")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # دانلود عکس
    photo_file = await update.message.photo[-1].get_file()
    bio = BytesIO()
    await photo_file.download_to_memory(out=bio)
    bio.seek(0)

    img = Image.open(bio)
    watermark = Image.open(WATERMARK_PATH)

    # اضافه کردن واترمارک
    result = add_watermark(img, watermark, scale=0.4)

    # ارسال مجدد
    out_bio = BytesIO()
    result.save(out_bio, format="JPEG")
    out_bio.seek(0)
    await update.message.reply_photo(photo=out_bio)

if __name__ == "__main__":
    # Get token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN") # Changed this line
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        exit(1)

    app = ApplicationBuilder().token(token).build()
    

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.run_polling()