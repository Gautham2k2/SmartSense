
from roboflow import Roboflow
import os
from ultralytics import YOLO
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("roboflow_api_key")

os.environ['CUDA_VISIBLE_DEVICES'] = '2,3'


rf = Roboflow(api_key=secret_key)
project = rf.workspace("gauthams-workspace").project("my-first-project-4sbu2")
version = project.version(4)
dataset = version.download("yolov8")

data_yaml_path = os.path.join(dataset.location, "data.yaml")

def train_floorplan_model():

    print(f"Trainig started... Using data from the path: {data_yaml_path}")

    model = YOLO('yolov8l.pt') 

    results = model.train(
        data=data_yaml_path,
        epochs=100,
        imgsz=512,
        project="floorplan_training",
        name="run_1",
    )

    print("Training is fully complete.")
    save_dir = model.trainer.save_dir
    print(f"Model saved to: {save_dir}")
    print(f"The best model is in the path: {save_dir}/weights/best.pt")


if not os.path.exists(data_yaml_path):
    print(f"Error: Could not find '{data_yaml_path}'.")
    print("Please download your dataset from Roboflow and update the 'data_yaml_path' variable.")
else:
    train_floorplan_model()



                