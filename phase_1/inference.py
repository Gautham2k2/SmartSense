import json
from collections import defaultdict
import os 
from ultralytics import YOLO

MODEL_PATH = r"C:\Users\gauth\OneDrive\Documents\SmartSense\phase_1\floorplan_training\run_1\weights\best.pt"

def parse_floorplan(image_path: str) -> str:
    try:
        model = YOLO(MODEL_PATH)
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_PATH}")
        print("Please make path is correct.")
        return json.dumps({"error": f"Model file not found at {MODEL_PATH}"})
    except Exception as e:
         return json.dumps({"error": f"Error loading model: {e}"})

    print(f"Parsing {image_path}...")
    
    try:
        results = model(image_path)
    except Exception as e:
        print(f"Error during model inference: {e}")
        return json.dumps({"error": str(e)})

    model_class_names = model.names
    
    final_counts = defaultdict(int)

    for result in results:
        if result.boxes:
            for box in result.boxes:
                class_index = int(box.cls)
                detected_class_name = model_class_names[class_index]
                
                final_counts[detected_class_name] += 1

    return json.dumps(final_counts, indent=2)


if __name__ == '__main__':
    if not os.path.exists(MODEL_PATH):
        print(f"Model file {MODEL_PATH} not found.")

    example_image_path = "/home/gauthambharati/SmartSense/phase_1/My-First-Project-4/test/images/68_21_jpg.rf.b96c5c0248796e29350c3d078f7ee2d7.jpg" 

    if os.path.exists(example_image_path):
        json_output = parse_floorplan(example_image_path)
        print("\n--- Output JSON is being created ---")
        print(json_output)
        output_path = "inference_output.json"
        with open(output_path, "w") as f:
            f.write(json_output)
        print(f"\nJSON output saved to: {output_path}")
    else:
        print(f"\nError: Example image '{example_image_path}' not found.")
        print("Please update 'example_image_path' to test (infer) the script.")

    
