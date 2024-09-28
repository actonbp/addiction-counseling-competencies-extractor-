import os
import base64
import requests
from tqdm import tqdm
import json

# OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_image(image_path):
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the Competency number, title, and the Knowledge, Skills, and Attitudes sections from this image. Format the output as plain text."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print(f"Response content: {response.text}")
        return None

    result = response.json()
    
    if 'error' in result:
        print(f"API Error: {result['error']}")
        return None

    if 'choices' in result and len(result['choices']) > 0:
        content = result['choices'][0]['message']['content']
        return content.strip()
    else:
        print(f"Unexpected API response format: {result}")
        return None

def process_all_images(folder_path):
    results = {}
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]

    for image_file in tqdm(image_files, desc="Processing images"):
        image_path = os.path.join(folder_path, image_file)
        result = process_image(image_path)
        
        if result is None:
            print(f"Skipping {image_file} due to processing error")
            continue
        
        print(f"Successfully processed {image_file}")
        print(f"Extracted content:\n{result[:200]}...")  # Print first 200 characters
        results[image_file] = result

    return results

def save_results(results, output_file):
    with open(output_file, 'w') as f:
        for image_file, content in results.items():
            f.write(f"File: {image_file}\n")
            f.write(f"{content}\n")
            f.write("-" * 80 + "\n\n")

if __name__ == "__main__":
    input_folder = "outputs"  # Folder containing the PNG images
    output_file = "competencies_from_images.txt"

    results = process_all_images(input_folder)
    save_results(results, output_file)
    print(f"Results saved to {output_file}")