import os
import openai
import fitz  # PyMuPDF
import re
from tqdm import tqdm
import aiohttp
import random

# Set OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')


# Function to call OpenAI and get KSA sections
async def call_openai_for_ksa(text_block):
    prompt = f"""
    Extract the following text and organize it into three sections: Knowledge, Skills, and Attitudes. 
    If any section is missing, mark it as "None". 

    Here's an example of the expected output format for Competency 1 (this is the exact answer for competency 1):

    Knowledge:
    • Terms and concepts related to theory, etiology, research, and practice.
    • Scientific and theoretical basis of model from medicine, psychology, sociology, religious studies, and other disciplines.
    • Criteria and methods for evaluating models and theories.
    • Appropriate applications of models.
    • How to access addiction-related literature from multiple disciplines.

    Skills:
    None

    Attitudes:
    • Openness to information that may differ from personally held views.
    • Appreciation of the complexity inherent in understanding addiction.
    • Valuing of diverse concepts, models, and theories.
    • Willingness to form personal concepts through critical thinking.

    Now, extract the Knowledge, Skills, and Attitudes from the following text:

    Text: 
    {text_block}

    Output format:
    Knowledge:
    • [list of knowledge items]
    
    Skills:
    • [list of skills]
    
    Attitudes:
    • [list of attitudes]
    """

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions', json={
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts Knowledge, Skills, and Attitudes from text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }, headers={
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }) as response:
            data = await response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                print(f"Unexpected API response: {data}")
                return "Error: Unable to process the response"


# Extract text with positions from PDF (this part remains the same)
def extract_text_with_positions(pdf_path):
    doc = fitz.open(pdf_path)
    text_with_positions = []
    for page in tqdm(doc, desc="Extracting text from PDF"):
        blocks = page.get_text("blocks")
        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            text_with_positions.append((text.strip(), y0, x0, page.number))
    return sorted(text_with_positions, key=lambda x: (x[3], x[1], x[2]))


# Group by competency and call OpenAI API for KSA extraction
async def group_by_competency(text_with_positions):
    competencies = {}
    current_competency = None
    buffer_text = ""

    for text, y_pos, x_pos, page_num in tqdm(
        text_with_positions, desc="Grouping competencies"
    ):
        competency_match = re.match(r"Competency (\d+):", text)

        if competency_match:
            if current_competency:
                print(f"\nInput text for {current_competency}:")
                print(buffer_text)
                ksa_sections = await call_openai_for_ksa(buffer_text)
                print(f"\nOpenAI output for {current_competency}:")
                print(ksa_sections)
                competencies[current_competency].update(parse_ksa_sections(ksa_sections))

            current_competency = f"Competency {competency_match.group(1)}"
            competencies[current_competency] = {
                "Title": text,
                "Knowledge": [],
                "Skills": [],
                "Attitudes": [],
            }
            buffer_text = ""
            print(f"\nFound {current_competency}")

        if current_competency:
            buffer_text += f"{text}\n"

    if current_competency:
        print(f"\nInput text for {current_competency}:")
        print(buffer_text)
        ksa_sections = await call_openai_for_ksa(buffer_text)
        print(f"\nOpenAI output for {current_competency}:")
        print(ksa_sections)
        competencies[current_competency].update(parse_ksa_sections(ksa_sections))

    return competencies


# Helper function to parse KSA sections from OpenAI response
def parse_ksa_sections(ksa_text):
    ksa_data = {"Knowledge": [], "Skills": [], "Attitudes": []}
    current_section = None
    current_subsection = None

    for line in ksa_text.splitlines():
        line = line.strip()
        if line in ["Knowledge", "Skills", "Attitudes"]:
            current_section = line
            current_subsection = None
        elif current_section:
            if line.startswith("•") or (not line.startswith("-") and not current_subsection):
                current_subsection = line.lstrip("• ")
                ksa_data[current_section].append({current_subsection: []})
            elif current_subsection and (line.startswith("-") or line.startswith("–")):
                ksa_data[current_section][-1][current_subsection].append(line.lstrip("-– ").strip())

    return ksa_data


# Format the output (this part remains the same)
def format_output(competencies):
    output = ""
    for competency, sections in tqdm(
        sorted(competencies.items(), key=lambda x: int(x[0].split()[1])),
        desc="Formatting output",
    ):
        output += f"{sections['Title']}\n"
        for section in ["Knowledge", "Skills", "Attitudes"]:
            output += f"  - {section}:\n"
            if sections[section]:
                for item in sections[section]:
                    output += f"    - {item}\n"
            else:
                output += f"    [No {section.lower()} section for this competency]\n"
        output += "\n"
    return output


# Main function to process PDF and extract KSAs
async def main():
    pdf_path = "sample.pdf"  # Replace with your PDF file name
    print(f"Processing PDF: {pdf_path}")

    text_with_positions = extract_text_with_positions(pdf_path)
    print(f"Extracted {len(text_with_positions)} text blocks")

    competencies = await group_by_competency(text_with_positions)
    print(f"Found {len(competencies)} competencies")

    formatted_output = format_output(competencies)

    output_file = "competencies_output.txt"
    with open(output_file, "w", encoding="utf-8") as output_file:
        output_file.write(formatted_output)
    print(f"Extraction complete. Results written to {output_file}")
    print(f"Total competencies processed: {len(competencies)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
