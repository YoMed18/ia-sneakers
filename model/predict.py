from ultralytics import YOLO
from PIL import Image
import io

model = YOLO('model/runs/detect/train28/weights/best.pt', 'detect')


def predict_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    result = model(image)[0]
    return result.names[0]