from ultralytics import YOLO

model = YOLO('../yolov8n.pt')

results = model.train(
    data='../datatset/data.yaml',
    epochs=200
)

results = model.val()

successes = model.export(format='onnx')
