from ultralytics import YOLO

class YOLOModel:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def predict(self, img):
        results = self.model.predict(img)
        return results
