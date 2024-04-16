from PIL import Image
import cv2


from numpy import ndarray
from typing import Union


COLOR_LIST = [
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 0, 0),
    (128, 255, 128),
    (255, 128, 128),
    (128, 128, 255),
    (128, 128, 128),
]

import math
import numpy as np


class Visualizer:
    def __init__(self):
        pass

    def draw_rect(
        self, image: Union[str, ndarray], rect: dict, color=(0, 0, 255), thickness=5
    ):
        """
        Draw rectangle on image
        """
        if isinstance(image, str):
            image = cv2.imread(image)

        left = rect["left"]
        top = rect["top"]
        right = left + rect["width"]
        bottom = top + rect["height"]
        cv2.rectangle(image, (left, top), (right, bottom), color, thickness)

        return image

    def reflow_block(self, source_image: ndarray, blocks: dict):
        output_image = np.zeros(source_image.shape, dtype=np.uint8)
        output_image.fill(255)
        pos_y = 100

        blocks = sorted(
            blocks,
            key=lambda x: x["rect"]["top"] + int(x["rect"]["height"] / 1000) * 1000,
        )

        for block in blocks:
            rect = block["rect"]

            if pos_y + rect["height"] > output_image.shape[0]:
                # extends height of output image
                extends = np.zeros(
                    (
                        rect["height"] + pos_y - output_image.shape[0],
                        output_image.shape[1],
                        3,
                    ),
                    dtype=np.uint8,
                )
                extends.fill(255)
                output_image = np.concatenate([output_image, extends], axis=0)

            output_image[pos_y : pos_y + rect["height"], 0 : rect["width"]] = (
                source_image[
                    rect["top"] : rect["top"] + rect["height"],
                    rect["left"] : rect["left"] + rect["width"],
                ]
            )
            pos_y += rect["height"] + 100

        return output_image

    def reflow_block_pf2(self, source_image: ndarray, blocks: dict, dpi=300):
        blocks = [
            {
                "rect": {
                    "left": int(block["region"]["x1"] * dpi / 72),
                    "top": int(block["region"]["y1"] * dpi / 72),
                    "width": int(
                        block["region"]["x2"] - block["region"]["x1"] * dpi / 72
                    ),
                    "height": int(
                        block["region"]["y2"] - block["region"]["y1"] * dpi / 72
                    ),
                },
            }
            for block in blocks
        ]
        return self.reflow_block(source_image, blocks)

    def draw_ocr_output(self, image, output: dict):
        for block in output:
            # self.draw_rect(image, block['rect'])

            for par in block["children"]:
                block_num = par["index"]["block_num"] % len(COLOR_LIST)
                # self.draw_rect(image, par['rect'], color=COLOR_LIST[block_num], thickness=3)
                for line in par["children"]:
                    if "font_size" not in line:
                        continue
                    # par_num = line['index']['par_num'] % len(COLOR_LIST)
                    font_size = round(line["font_size"] / 4) % len(COLOR_LIST)
                    self.draw_rect(
                        image, line["rect"], COLOR_LIST[font_size], thickness=1
                    )

        return image

    def draw_ocr_output_from_path(self, image_path, output: dict):
        image = cv2.imread(image_path)
        image = self.draw_ocr_output(image, output)
        # save image
        cv2.imwrite(image_path.replace(".png", "_output.png"), image)

    def draw_ocr_output_from_list(self, images, outputs, output_path):
        for i in range(len(images)):
            image = images[i]
            output = outputs[i]
            image = self.reflow_block(image, output)
            # image = self.draw_ocr_output(image, output)
            # save image
            cv2.imwrite(output_path.replace(".png", f"_output_{i}.png"), image)
