import json
import os

def main():
    # Path to the JSON file
    # This constructs the path relative to where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'PiCamera', 'box_coords.json')

    if not os.path.exists(json_path):
        print(f"Error: Could not find {json_path}")
        print("Make sure you have run the detection script first.")
        return

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        if "detection" in data:
            detection = data["detection"]
            xyxy = detection.get("xyxy", [])
            conf = detection.get("conf", 0)
            
            print("-" * 30)
            print("Face Detection Results")
            print("-" * 30)
            print(f"Timestamp: {data.get('datetime_local', 'Unknown')}")
            print(f"Confidence: {conf:.2%}")
            
            if xyxy:
                print(f"Bounding Box: {xyxy}")
                # Calculate center
                center_x = (xyxy[0] + xyxy[2]) / 2
                center_y = (xyxy[1] + xyxy[3]) / 2
                print(f"Center Position: ({center_x:.1f}, {center_y:.1f})")
                
                width = xyxy[2] - xyxy[0]
                height = xyxy[3] - xyxy[1]
                print(f"Dimensions: {width:.1f} x {height:.1f}")
            else:
                print("No bounding box coordinates found.")
            print("-" * 30)
        else:
            print("No detection data found in the file.")

    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
