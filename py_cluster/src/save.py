import numpy as np
import json
from typing import List
from PIL import Image, ImageDraw
from .custom_types import ClusterType


def save_to_img(img: np.ndarray, clusters: List[ClusterType], save_path: str):
    """
        Draws rectangles around detected clusters on an image and saves the result to a file.

        Parameters
        ----------
        img : np.ndarray
            The input image as a NumPy array (typically grayscale or RGB).
        clusters : List[ClusterType]
            A list of cluster bounding boxes with format:
            [((min_i, min_j), (max_i, max_j), label)], where label is typically the pixel count.
        save_path : str
            File path where the output image with drawn rectangles should be saved.

        Notes
        -----
        The function uses PIL to draw red rectangles around each detected cluster.
        Coordinate axes are switched due to difference in PIL and NumPy (row ↔ column).
        """
    # Convert np image to PIL Image
    img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)

    for cluster in clusters:
        top_left, bottom_right, label = cluster
        # we have to switch x with y, because of missmatch witch different coordinate system
        draw.rectangle([(top_left[1], top_left[0]), (bottom_right[1], bottom_right[0])], outline="red", width=1)

    img.save(save_path)


def save_clusters(clusters: List[ClusterType], file_name: str = "data", /, *, file_format: str = "csv") -> None:
    """
      Saves the cluster data to a file in the specified format (CSV or JSON). Optionally supports 'img'.

      Parameters
      ----------
      clusters : List[ClusterType]
          A list of clusters represented as:
          [((min_i, min_j), (max_i, max_j), pixel_count)].
      file_name : str, optional
          The base name of the output file (without extension). Default is "data".
      file_format : str, optional
          The desired output format: "csv", "json", or "img". Default is "csv".

      Raises
      ------
      Warning
          If the file format is not supported, falls back to CSV with a warning.

      Notes
      -----
      - JSON format stores structured cluster data with keys.
      - CSV format saves rows of raw numbers: min_x, min_y, max_x, max_y, pixel_count.
      - 'img' format is intended for visual export, but must be handled separately.
      """
    match file_format.lower():
        case "json":
            cluster_data = [{'min_x': min_i, 'min_y': min_j, 'max_x': max_i, 'max_y': max_j, 'pixel_count': pixel_count}
                            for (min_i, min_j), (max_i, max_j), pixel_count in clusters]

            with open(file_name + '.json', 'w') as file:
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
