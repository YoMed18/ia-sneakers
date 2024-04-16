from ultralytics import YOLO

model = YOLO('../yolov8n.pt')


def train_model(data, epochs):
    results = model.train(
        data=data,
        epochs=epochs
    )


successes = model.export(format='onnx')
