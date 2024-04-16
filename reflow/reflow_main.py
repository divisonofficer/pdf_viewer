

from ocr import TesseractOCRModule
from visualizer import Visualizer
from ocr_data_formatter import OCRDataFormatter
from pdf_png_converter import PdfPngConverter
from figure_extract import FigureExtractor



import sys
import cv2

if __name__ == '__main__':
    pdf_path = sys.argv[1]
    save_path = sys.argv[2] if len(sys.argv) > 2 else pdf_path.replace(".pdf", ".png")
    pdf_png_converter = PdfPngConverter()
    images = pdf_png_converter.read_pdf_file_and_convert_to_bitmap(pdf_path)
    
    figure_extractor = FigureExtractor()
    
    images = figure_extractor.mask_figure_on_image(images, figure_extractor.extract_figure_from_pdf_path(pdf_path))
    
    for (i, image) in enumerate(images):
         cv2.imwrite(f'{save_path}_{i}.png', image)
    
    
    
    tesseract = TesseractOCRModule()
    output = tesseract.extract_text_rect_from_list(images)
    formatter = OCRDataFormatter()
    output = formatter.format_output_to_hirerachy(output)
    
    with open(save_path.replace('.png', '_ocr.json'), 'w') as f:
        f.write(str(output))
    
    visualizer = Visualizer()
    
    visualizer.draw_ocr_output_from_list(images, output, save_path)
    
