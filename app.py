import requests
import json
import re

headers = {
    "Content-Type": "application/json"
}

def translate_text(text, headers, target_language="am"):
    payload = {
        "content": text,
        "format": "text",
        "source_language": "en",
        "target_language": target_language
    }
    try:
        response = requests.post("https://translate.wmcloud.org/api/translate", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        translation = response.json().get('translation', '')
        return translation.replace("'", '').replace('፣', '')
    except requests.exceptions.RequestException as e:
        print(f"Translation error: {e}")
        return text

def process_srt_in_chunks(input_file, output_file, headers, target_language="am", chunk_size=5000):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            lines = infile.readlines()
            i = 0
            while i < len(lines):
                if lines[i].strip().isdigit():
                    subtitle_number = lines[i].strip()
                    timestamp = lines[i+1].strip()
                    text_lines = []
                    j = i + 2
                    while j < len(lines) and lines[j].strip():
                        text_lines.append(lines[j].strip())
                        j += 1

                    original_text = "\n".join(text_lines)
                    translated_chunks = []
                    start = 0
                    while start < len(original_text):
                        end = min(start + chunk_size, len(original_text))
                        chunk = original_text[start:end]
                        translated_chunk = translate_text(chunk, headers, target_language)
                        translated_chunks.append(translated_chunk)
                        start = end

                    translated_text = "".join(translated_chunks)

                    outfile.write(f"{subtitle_number}\n")
                    outfile.write(f"{timestamp}\n")
                    outfile.write(f"{translated_text}\n\n")

                    i = j + 1
                else:
                    outfile.write(lines[i]) # Write non-subtitle lines as is
                    i += 1

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    input_srt_file = 'cobra_kai.srt'
    output_srt_file = 'new_cobra_kai.srt'
    target_language = 'am'
    chunk_size = 5000  # Set your desired chunk size

    process_srt_in_chunks(input_srt_file, output_srt_file, headers, target_language, chunk_size)
    print(f"Translated SRT written to '{output_srt_file}' in chunks.")