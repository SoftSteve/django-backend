import io, pathlib
from PIL import Image, ExifTags
from django.core.files.base import ContentFile

QUALITY = 90  # JPEG quality


def compress_in_memory(upload):
    """Return a fresh Django ContentFile ( <bytes>, name ) ready for model save.
    ➤ Keeps original resolution (no down‑scaling) ‑ just orientation fix + JPEG recompress.
    """
    img = Image.open(upload)

    # --- Fix orientation from EXIF ---
    try:
        orient_key = next(k for k, v in ExifTags.TAGS.items() if v == "Orientation")
        orient = img._getexif().get(orient_key, 1) if img._getexif() else 1
        rotations = {3: 180, 6: 270, 8: 90}
        if orient in rotations:
            img = img.rotate(rotations[orient], expand=True)
    except Exception:
        pass

    # --- Convert & save ---
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=QUALITY, optimize=True)
    buf.seek(0)

    new_name = f"{pathlib.Path(upload.name).stem}.jpg"
    return ContentFile(buf.read(), name=new_name)