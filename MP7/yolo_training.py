# Copilot prompt:
# Write code to install and import all necessary libraries for training a YOLO model using Ultralytics in Google Colab.
# Include: ultralytics, torch, matplotlib, gradio.

# Install required packages

# Import necessary libraries
import torch
import torchvision
import matplotlib.pyplot as plt
import gradio as gr
from ultralytics import YOLO
import cv2
import numpy as np
import os
import yaml
from PIL import Image
import random
from pathlib import Path
import ultralytics

if __name__ == '__main__':
    # Fix for Windows: disable pinning memory for data loader
    torch.multiprocessing.freeze_support()
        
    print("All libraries installed and imported successfully!")
    print(f"Ultralytics version: {ultralytics.__version__ if 'ultralytics' in globals() else 'Not available'}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Matplotlib version: {plt.matplotlib.__version__}")
    print(f"OpenCV version: {cv2.__version__}")

    # Copilot prompt:
    # Load the latest YOLO model (e.g., yolov11n.pt if available, otherwise yolov8n.pt) using the Ultralytics library.
    # Show the model summary.


    # configurations
    dataset_path = ".././data/mp7/dataset_complete_v4"
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    train_project='MP7_Object_Detection'
    train_name='v4dataset_yolov11n_augmented'
    model_name = "C:\\Users\\jhon\\Desktop\\Coding\\AI\\AI231-machine-problems\\MP7\\MP7_Object_Detection\\v2dataset_yolov11n_augmented3\\weights\\best.pt"  # Change to "yolov8n.pt" if yolov11n is not available
    data_yml_path = os.path.join(dataset_path, 'data.yaml')
    
    # Set Windows-specific PyTorch settings
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        # Disable pin_memory on Windows to avoid shared memory issues
        torch.multiprocessing.set_sharing_strategy('file_system')

    # Load class names from data.yaml
    with open(data_yml_path, 'r') as f:
        data_yaml = yaml.safe_load(f)
        class_names = data_yaml.get('names', [])
        print(f"Loaded {len(class_names)} classes from data.yaml")

    # Try to load the latest YOLO model
    def load_yolo_model():      
        try:
            # Try YOLOv11n first (latest)
            model = YOLO(model=model_name)
            print("Loaded MP4 Best model successfully!")
        except:
            print("Error loading YOLO model. Please check your internet connection.")

        if model is not None:
            # Show model information
            print(f"\nModel architecture: {model.model}")
            print(f"Model task: {model.task}")
            
            # Print model summary
            model.info(detailed=True)
            
            print(f"\nModel loaded successfully and ready for training!")
        else:
            print("Failed to load YOLO model.")
        return model


    model = load_yolo_model()

    results = model.train(
        data=f"{dataset_path}/data.yaml",
        epochs=100,
        imgsz=640,
        batch=8,
        device=device,
        project=train_project,
        name=train_name,
        save=True,
        cache=False,  # Disable cache on Windows to avoid memory issues
        workers=0,  # Set to 0 on Windows to avoid shared memory errors
        patience=50,  # Early stopping patience
        save_period=50,  # Save checkpoint every 50 epochs
        degrees=10,
        translate=0.1,
        scale=0.1,
        hsv_s=0.2,
        hsv_v=0.2,
        mosaic=0.5,
        fliplr=0.5,
        # hsv_s=0.1,  # Enable HSV saturation augmentation
        # hsv_h=0.1,  # Enable HSV Hue Adjustment
        # hsv_v=0.1,  # Enable HSV Value Adjustment
        # degrees=90.0,  # Enable rotation augmentation
        # translate=0.1,  # Translation augmentation
        # scale=0.1,  # Scale augmentation
        # shear=10.0,  # Shear augmentation
        # perspective=0.001,  # Perspective augmentation
        # flipud=0.05,  # Enable vertical flip augmentation (5% chance)
        # fliplr=0.05,  # Enable horizontal flip augmentation (5% chance)
        # bgr=0.05, # Enable BGR augmentation (5% chance)
        # mosaic=0.5,  # Mosaic augmentation (50% chance of being combined with three other images)
        # mixup=0.5,  # Mixup augmentation (30% chance of being blended with another image),
        # cutmix=0.5,  # CutMix augmentation (50% chance of being combined with another image)
        # copy_paste=0.5,  # Copy-paste augmentation (50% chance of copying objects from another image)
        # copy_paste_mode='mixup', # Copy-paste mode (mixup allows objectys to be copied from different images)
        # erasing=0.0  # Random Erasing augmentation (40% chance of random erasing)
    )
    
    print("Training completed successfully!")
    print(f"Results saved to: {results.save_dir}")
    print(f"Best model weights: {results.save_dir}/weights/best.pt")
    print(f"Last model weights: {results.save_dir}/weights/last.pt")

    training_results = results


    def evaluate_model(training_results, dataset_path):
        try:
            # Load the best trained model
            best_model_path = f"{training_results.save_dir}/weights/best.pt"
            trained_model = YOLO(best_model_path)
            
            print("Evaluating the trained model on test dataset...")
            
            # Evaluate on test dataset
            eval_results = trained_model.val(data=f"{dataset_path}/data.yaml")
            
            print("\n" + "="*50)
            print("MODEL EVALUATION RESULTS")
            print("="*50)
            
            # Extract and print key metrics
            if hasattr(eval_results, 'box'):
                metrics = eval_results.box
                print(f"mAP50 (IoU=0.5): {metrics.map50:.4f}")
                print(f"mAP50-95 (IoU=0.5:0.95): {metrics.map:.4f}")
                print(f"Precision: {metrics.mp:.4f}")
                print(f"Recall: {metrics.mr:.4f}")
                
            # Print class-wise metrics if available
            if hasattr(eval_results, 'box') and hasattr(eval_results.box, 'ap_class_index'):
                ap_class_index = eval_results.box.ap_class_index
                # print attributes of eval_results 
                print(dir(eval_results))
                if len(ap_class_index) > 0:
                    print("\nClass-wise mAP50:")
                    # Get the mAP values per class
                    maps = eval_results.box.maps  # This gives mAP50 per class
                    for i, class_idx in enumerate(ap_class_index):
                        class_name = class_names[class_idx] if class_idx < len(class_names) else f'class_{class_idx}'
                        if i < len(maps):
                            print(f"  {class_name}: {maps[i]:.4f}")
                        else:
                            print(f"  {class_name}: N/A")
            
            print(f"\nEvaluation completed!")
            print(f"Results saved to: {eval_results.save_dir}")
            
        except Exception as e:
            print(f"Evaluation failed: {str(e)}")
            print("Please ensure training was completed successfully.")