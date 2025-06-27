import io, pathlib
from PIL import Image, ExifTags
from django.core.files.base import ContentFile

MAX_W    = 1600        
QUALITY  = 90            

def compress_in_memory(upload):
    """Return a fresh Django ContentFile (<bytes>, name) ready for model save."""
    img = Image.open(upload)

    try:
        orient_key = next(k for k, v in ExifTags.TAGS.items() if v == "Orientation")
        orient = img._getexif().get(orient_key, 1) if img._getexif() else 1
        if orient == 3:  img = img.rotate(180, expand=True)
        elif orient == 6: img = img.rotate(270, expand=True)
        elif orient == 8: img = img.rotate( 90, expand=True)
    except Exception:
        pass

    if img.width > MAX_W:
        ratio = MAX_W / img.width
        img = img.resize((MAX_W, int(img.height * ratio)), Image.LANCZOS)

    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=QUALITY, optimize=True)
    buf.seek(0)

    new_name = f"{pathlib.Path(upload.name).stem}.jpg"
    return ContentFile(buf.read(), name=new_name)