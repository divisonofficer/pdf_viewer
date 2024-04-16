import fitz
from PIL import Image
import os
import sys
import cv2

try:
    from config import config
except:
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(f'{current_path}/..')
    from config import config

class PdfPngConverter:
    def __init__(self):
        pass

    def read_pdf_file_and_convert_to_png(self, file_path, dpi=300):
        """
        Read PDF file and convert to PNG
        """
        # Read PDF file
        pdf = fitz.open(file_path)
        # Convert to PNG
        pages = self.convert_pdf_to_png(pdf, dpi)
        pdf.close()

        return pages

    def read_pdf_file_and_convert_to_bitmap(self, file_path, dpi=300):
        '''
        Read PDF file and convert to bitmap
        @param file_path: PDF file path
        @param dpi: DPI
        '''
        
        TEMP_FOLDER = config.PDF_TEMP_ROOT
        TEMP_LOCATION = f'{TEMP_FOLDER}/temp.pdf'
        
        ### if no temp folder, create one
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)
        ### void the folder
        for file in os.listdir(TEMP_FOLDER):
            os.remove(f'{TEMP_FOLDER}/{file}')
            
        ### Save PDF to Temp Folder
        self.read_pdf_file_and_save_to_png(file_path, TEMP_LOCATION, dpi)
        
        images = []
        files = os.listdir(TEMP_FOLDER)
        files.sort(key=lambda file: int(file.split('_')[-1].split('.')[0]))
        for file in files:
            if file.endswith('.png'):
                images.append(cv2.imread(f'{TEMP_FOLDER}/{file}'))
        
        
        return images

    def read_pdf_file_and_save_to_png(self, file_path, save_path, dpi=300):
        '''
        Read PDF file and save to PNG
        @param file_path: PDF file path
        @param save_path: Save path
        @param dpi: DPI
        '''
        pages = self.read_pdf_file_and_convert_to_png(file_path, dpi)
        self.save_pages_as_png(pages, save_path)

    def save_pages_as_png(self, pages: list, file_path: str):
        """
        Save pages as PNG
        """
        file_path = file_path.split(".")[0]
        for i, page in enumerate(pages):
            page.save(f"{file_path}_{i}.png")

    def convert_pdf_to_png(self, pdf: fitz.Document, dpi=300):
        """
        Convert PDF to PNG
        """
        # Convert to PNG
        pages = []
        for page_number in range(pdf.page_count):
            page = pdf.load_page(page_number)
            # Calculate the scale factor for the desired DPI
            scale = dpi / 72
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
            pages.append(pix)

        return pages




if __name__ == "__main__":
    pdf_png_converter = PdfPngConverter()
    pdf_path = sys.argv[1]
    save_path = sys.argv[2] if len(sys.argv) > 2 else pdf_path.replace(".pdf", ".png")
    pdf_png_converter.read_pdf_file_and_save_to_png(pdf_path, save_path)
    #pages = pdf_png_converter.read_pdf_file_and_convert_to_bitmap(pdf_path)

    print("PDF to PNG conversion is done.")