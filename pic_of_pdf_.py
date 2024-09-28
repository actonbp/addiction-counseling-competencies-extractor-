import os
import fitz  # PyMuPDF
from PIL import Image
from tqdm import tqdm
import re

def extract_text_with_positions(pdf_path):
    doc = fitz.open(pdf_path)
    text_with_positions = []
    for page in tqdm(doc, desc="Extracting text from PDF"):
        blocks = page.get_text("blocks")
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            text_with_positions.append((text.strip(), y0, x0, page.number))
    return sorted(text_with_positions, key=lambda x: (x[3], x[1], x[2]))

def generate_pdf_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    
    text_with_positions = extract_text_with_positions(pdf_path)
    pages_with_competencies = set()

    for text, _, _, page_num in text_with_positions:
        if re.search(r"Competency|Know|Skil|Attit", text, re.IGNORECASE):
            pages_with_competencies.add(page_num)

    for page_num in tqdm(pages_with_competencies, desc="Generating images"):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        img.save(img_path)

    print(f"Generated {len(pages_with_competencies)} images in {output_folder}")

if __name__ == "__main__":
    pdf_path = "sample.pdf"  # Replace with your PDF file name
    output_folder = "outputs"
    
    generate_pdf_images(pdf_path, output_folder)
