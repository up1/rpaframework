import base64
import io
from PIL import Image


def image_to_base64(image):
    """Convert Image object to base64 string."""
    stream = io.BytesIO()
    image.save(stream)
    data = stream.getvalue()
    text = base64.b64encode(data)
    return text


def base64_to_image(text):
    """Convert image in base64 string to Image object."""
    data = base64.b64decode(text)
    stream = io.BytesIO(data)
    image = Image.open(stream)
    return image
