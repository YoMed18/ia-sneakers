from ultralytics import YOLO
from PIL import Image
import io

model = YOLO('model/runs/detect/train28/weights/best.pt')


def predict_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    model.predict(image)
    label_name = model.names[0]
    print(f"Label: {label_name}")
    return label_name



