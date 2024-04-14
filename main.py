import fitz
import subprocess
import sys
import os
import json
import cv2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'ScanSSD')))

from ssd import build_ssd
from data import exp_cfg
from torch import nn
import numpy as np

def read_pdf_file_and_convert_to_png(file_path, dpi = 300):
    """
    Read PDF file and convert to PNG
    """
    # Read PDF file
    pdf = fitz.open(file_path)
    # Convert to PNG
    sample_name = file_path.split(".")[0]

    for page_number in range(pdf.page_count):
        page = pdf.load_page(page_number)
            # Calculate the scale factor for the desired DPI
        scale = dpi / 72  # Default DPI in PyMuPDF is 72
        
        # Create a transformation matrix for the desired scaling
        mat = fitz.Matrix(scale, scale)
        
        # Render the page to an image (pixmap)
        pix = page.get_pixmap(matrix=mat)
        
        # Save the image
        pix.save(f"{sample_name}_page_{page_number}.png")
    pdf.close()


def extract_features_from_pdf(pdf_path):
    command = f'java -cp pdffigure.jar org.allenai.pdffigures2.FigureExtractorBatchCli -m "" -g "" "{pdf_path}"'
    subprocess.run(command, shell=True)


def draw_single_box_on_image(pdf_path, page_num, box_rect, box_color, dpi = 300):
    image_path = pdf_path.replace(".pdf", f"_page_{page_num}.png")
    image = cv2.imread(image_path)
    x1, y1, x2, y2 = box_rect["x1"], box_rect["y1"], box_rect["x2"], box_rect["y2"]
    x1 = int(x1 * dpi / 72)
    y1 = int(y1 * dpi / 72)
    x2 = int(x2 * dpi / 72)
    y2 = int(y2 * dpi / 72)
    cv2.rectangle(image, (x1, y1), (x2, y2), box_color, 2)
    cv2.imwrite(image_path, image)


def draw_boxes_on_pdf(pdf_path):
    json_path = pdf_path.replace(".pdf", ".json")
    with open(json_path, "r") as f:
        data = json.load(f)

        # draw abstract
        draw_single_box_on_image(pdf_path,
                                 data["abstractText"]["page"],
                                 data["abstractText"]["region"],
                                 (0, 0, 255))
        
        # draw figures

        for figure in data["figures"]:
            draw_single_box_on_image(pdf_path,
                                     figure["page"],
                                     figure["regionBoundary"],
                                     (0, 255, 0))
            
            draw_single_box_on_image(pdf_path,
                                     figure["page"],
                                     figure["captionBoundary"],
                                     (255, 0, 0))
            





def create_model(cuda=False):
    """
    Create the SSD model with the specified options.
    """
    class Args:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    args = Args(cfg='gtdb', model_type=512, cuda=cuda, trained_model='weights/ssd512_GTDB_990.pth',
                kernel = (1,3), padding = (0,1), stride = 0.1, window = 1200)
    num_classes = 2  # +1 background
    gpu_id = 0 if cuda else -1

    net = build_ssd(args, 'test', exp_cfg['gtdb'], gpu_id, 512, num_classes)
    if cuda:
        net = net.cuda()

    net = nn.DataParallel(net)
    net.eval()
    return net
model = create_model(cuda=True)

from PIL import Image
import torch

def extract_latex_from_pdf(pdf_path):
    png_path = pdf_path.replace(".pdf", "_page_2.png")
    image = Image.open(png_path)
    # resize to 1024 x 1024
    image = image.resize((1024, 1024))
    image = np.array(image)

    image = torch.from_numpy(image).float().unsqueeze(0).permute(0, 3, 1, 2)
    print(image.shape)
    model.eval()
    with torch.no_grad():
        result = model(image)
    print(result)




if __name__ == "__main__":
    sample = "Taniai_Maehara_2018_Neural Inverse Rendering for General Reflectance Photometric Stereo.pdf"
    #read_pdf_file_and_convert_to_png(sample)
    #extract_features_from_pdf(sample)
    #draw_boxes_on_pdf(sample)
    extract_latex_from_pdf(sample)




