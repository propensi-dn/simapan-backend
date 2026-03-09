from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import math


def add_watermark(image_file, text="SI-MAPAN - RAHASIA"):
    """
    Tambahkan watermark diagonal ke gambar KTP/selfie.
    Return: InMemoryUploadedFile yang siap disimpan ke model
    """
    img = Image.open(image_file).convert('RGBA')
    width, height = img.size

    watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    font_size = max(40, int(width / 10))
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width  = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    spacing_x = text_width + 80
    spacing_y = text_height + 60
    angle = 30

    for y in range(-height, height * 2, spacing_y):
        for x in range(-width, width * 2, spacing_x):
            txt_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((10, 10), text, font=font, fill=(255, 0, 0, 80))
            rotated = txt_img.rotate(angle, expand=True)
            watermark_layer.paste(rotated, (x, y), rotated)

    watermarked = Image.alpha_composite(img, watermark_layer)

    final_img = watermarked.convert('RGB')

    buffer = BytesIO()
    final_img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)

    return InMemoryUploadedFile(
        buffer,
        'ImageField',
        f"{image_file.name.split('.')[0]}_wm.jpg",
        'image/jpeg',
        sys.getsizeof(buffer),
        None
    )