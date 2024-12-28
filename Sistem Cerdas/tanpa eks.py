from ultralytics import YOLO

# Load the YOLO model
model = YOLO('best.pt')

# Perform prediction using the model
model.predict(source=0, imgsz=640, conf=0.6, show=True)
