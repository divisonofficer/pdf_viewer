import subprocess
import json
import os
import cv2

class FigureExtractor:
    def __init__(self):
        pass
    
    
    def extract_figure_from_pdf_path(self, pdf_path):
        folder_path = os.path.dirname(pdf_path)
        command = f'java -cp pdffigures2_pdj555.jar org.allenai.pdffigures2.FigureExtractorBatchCli -i 300 -m "{folder_path}/" -t 4 -g "{folder_path}/" "{pdf_path}"' # -m ""
        subprocess.run(command, shell=True)
        json_path = pdf_path.replace(".pdf", ".json")
        with open(json_path, "rb") as f:
            raw = f.read()
            data = json.loads(raw)
        
        return data
    
    def mask_figure_on_image(self, images, data, dpi = 300):
        for figure in data["figures"]:
            image_num = figure["page"]
            
            for rect in [figure["regionBoundary"], figure["captionBoundary"]]:
                x1, x2, y1, y2 = int(rect["x1"] * dpi / 72), int(rect["x2"] * dpi / 72), int(rect["y1"]* dpi / 72), int(rect["y2"]* dpi / 72)
                
                cv2.rectangle(images[image_num], (x1,y1),(x2,y2), (255, 255, 255), cv2.FILLED)
            
        return images
            
            
