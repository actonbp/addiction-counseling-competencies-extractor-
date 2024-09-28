import json
import re

def parse_competencies(file_path):
    competencies = []
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()

    # Replace any problematic characters that might interfere with parsing
    content = content.replace('\ufffd', '')

    # Split the content into competency blocks
    competency_blocks = re.split(r'\n(?=Competency \d+)', content)

    for block in competency_blocks:
        lines = block.strip().split('\n')
        if not lines or not re.match(r'^Competency \d+', lines[0]):
            continue

        # Extract competency ID
        id_match = re.match(r'Competency (\d+)', lines[0])
        if id_match:
            competency_id = int(id_match.group(1))
        else:
            continue

        # Initialize fields
        title = ''
        description = ''
        knowledge = []
        skills = []
        attitudes = []

        index = 1  # Start after 'Competency X' line

        # Extract title
        while index < len(lines) and not lines[index].strip():
            index += 1  # Skip empty lines

        if index < len(lines) and lines[index].startswith('Title:'):
            title = lines[index][6:].strip()
            index += 1
        else:
            # If there's no 'Title:' line, assume the next non-empty line is the title
            if index < len(lines):
                title = lines[index].strip()
                index += 1

        # Extract sections
        section = None
        section_content = []

        while index < len(lines):
            line = lines[index].strip()
            if line.endswith(':') and line[:-1] in ['Knowledge', 'Skills', 'Attitudes']:
                # Save previous section
                if section == 'Knowledge':
                    knowledge = section_content.copy()
                elif section == 'Skills':
                    skills = section_content.copy()
                elif section == 'Attitudes':
                    attitudes = section_content.copy()

                # Start new section
                section = line[:-1]
                section_content = []
            else:
                if line and not line.startswith('Competency'):
                    # Remove numbering or bullets
                    cleaned_line = re.sub(r'^(\d+\.\s*|\*\s*|\[\d+\])', '', line)
                    section_content.append(cleaned_line.strip())
            index += 1

        # Save the last section
        if section == 'Knowledge':
            knowledge = section_content.copy()
        elif section == 'Skills':
            skills = section_content.copy()
        elif section == 'Attitudes':
            attitudes = section_content.copy()

        # Create competency dictionary
        competency = {
            'id': competency_id,
            'title': title,
            'description': '',  # Description not provided separately in the text
            'knowledge': knowledge,
            'skills': skills,
            'attitudes': attitudes
        }

        competencies.append(competency)

    return competencies

if __name__ == '__main__':
    input_file = 'WFD_DC_KSAO_Clean.txt'
    output_file = 'competencies.json'
    competencies = parse_competencies(input_file)

    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(competencies, f, indent=4)

    print(f"Competencies have been successfully saved to {output_file}.")
