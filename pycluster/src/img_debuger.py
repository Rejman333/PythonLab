import os
import csv
from PIL import Image
from typing import List
import numpy as np
from numpy.typing import NDArray
from . custom_types import ClusterType
from . save import save_to_img, save_clusters

def save_debug_step(step_number: int, img: NDArray[np.uint8], clusters: List[ClusterType], base_dir: str = 'debug'):

    # Create base debug directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)

    # Create step subdirectory
    step_dir = os.path.join(base_dir, f'step{step_number}')
    os.makedirs(step_dir, exist_ok=True)

    # Save image with bounding boxes
    img_path = os.path.join(step_dir, 'image.png')
    save_to_img(img, [], img_path)

    img_path = os.path.join(step_dir, 'img_with_cluster.png')
    save_to_img(img, clusters, img_path)

    # Save clusters to CSV
    csv_path = os.path.join(step_dir, 'data.csv')
    save_clusters(clusters, csv_path[:-4], file_format="csv")  # bez rozszerzenia

    print(f"✔ Step {step_number} saved to: {step_dir}")