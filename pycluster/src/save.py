import numpy as np
import json
from typing import List
from PIL import Image, ImageDraw
from . custom_types import ClusterType


def save_to_img(img: np.ndarray, clusters: List[ClusterType], save_path: str):
    # Convert np image to PIL Image
    img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)

    for cluster in clusters:
        top_left, bottom_right, label = cluster
        # we have to switch x with y, because of missmatch witch different coordinate system
        draw.rectangle([(top_left[1], top_left[0]), (bottom_right[1], bottom_right[0])], outline="red", width=1)

    img.save(save_path)


def save_clusters(clusters: List[ClusterType], file_name: str = "data", /, *, file_format: str = "csv") -> None:
    match file_format.lower():
        case "json":
            cluster_data = [{'min_x': min_i, 'min_y': min_j, 'max_x': max_i, 'max_y': max_j, 'pixel_count': pixel_count}
                            for (min_i, min_j), (max_i, max_j), pixel_count in clusters]

            with open(file_name + 'json', 'w') as file:
                json.dump(cluster_data, file, indent=4)
            return
        case "csv":
            pass
        case "img":

            pass
        case _:
            raise Warning(f"File format: {file_format} not supported, using csv as default.")

    np.savetxt(file_name + '.csv',
               [[min_i, min_j, max_i, max_j, pixel_count] for (min_i, min_j), (max_i, max_j), pixel_count in clusters],
               delimiter=',', fmt="%d", header="min_x,min_y,max_x,max_y,pixel_count", comments="")
