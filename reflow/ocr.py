from PIL import Image
from pytesseract import pytesseract, Output
import os
import sys

try:
    from config import config
except:
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(f'{current_path}/..')
    from config import config


class TesseractOCRModule:
    def __init__(self):
        pass
    
    
    def extract_text_rect(self, image: Image):
        output = pytesseract.image_to_data(image, output_type=Output.DICT)
        return output
    
    def extract_text_rect_from_path(self, image_path):
        image = Image.open(image_path)
        return self.extract_text_rect(image)

    def extract_text_rect_from_list(self, image_list: list):
        result = []
        for image in image_list:
            result.append(self.extract_text_rect(image))
        return result
    
    
    
if __name__ == '__main__':
    tesseract = TesseractOCRModule()
    file_path = sys.argv[1]
    output = tesseract.extract_text_rect_from_path(file_path)
    from ocr_data_formatter import OCRDataFormatter
    from visualizer import Visualizer
    formatter = OCRDataFormatter()
    output = formatter.format_output_to_hirerachy(output)
    store_path = file_path.replace('.png', '.json')
    
    Visualizer().draw_ocr_output_from_path(file_path, output)
    
    with open(store_path, 'w') as f:
        f.write(str(output))
        