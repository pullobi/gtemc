import requests
import random, os
import time
LANG_CODES = [
    "af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca",
    "ceb", "ny", "zh-CN", "zh-TW", "co", "hr", "cs", "da", "nl", "en", "eo",
    "et", "tl", "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha",
    "haw", "he", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw",
    "kn", "kk", "km", "rw", "ko", "ku", "ky", "lo", "la", "lv", "lt", "lb",
    "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "or",
    "ps", "fa", "pl", "pt", "pa", "ro", "ru", "sm", "gd", "sr", "st", "sn",
    "sd", "si", "sk", "sl", "so", "es", "su", "sw", "sv", "tg", "ta", "tt",
    "te", "th", "tr", "tk", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi",
    "yo", "zu"
]

FILE_INPUT = "en_us.json"
FILE_OUTPUT = "gte.json"

NUM_CHUNKS = 16
FILE_INPUT_CHUNK_DIR = "source/"
FILE_OUTPUT_CHUNK_DIR = "dist/"

TRANSLATE_COUNT = 6



def write_log(string: str, file: str = "output.log"):
    with open(file, 'a', encoding='utf-8') as f:
        f.write(f"{string}\n")

# Google Translate Function
def google_translate(input_text: str, input_lang: str = "en", output_lang: str = "en") -> str:
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": input_lang,
        "tl": output_lang,
        "dt": "t",
        "q": input_text
    }
    response = requests.get(url, params=params)
    time.sleep(0.5)
    response.raise_for_status()
    result = response.json()
    return result[0][0][0]


def random_translate(input_text: str, input_lang: str, output_lang: str, count: int) -> str:
    
    text = input_text
    lang_in = input_lang
    lang_out= output_lang
    for i in range(0,count):
        random_lang = random.choice(LANG_CODES)
        text = google_translate(input_text=text, input_lang=lang_in, output_lang=random_lang)
        lang_in = random_lang
    text = google_translate(input_text=text, input_lang=lang_in, output_lang=lang_out)
    return text


import json
import os
import math
import concurrent.futures

def read_json(filename: str) -> dict[str, str]:
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


# Split a dict into n chunks
def split_dict(d: dict, n: int) -> list[dict]:
    items = list(d.items())
    chunk_size = math.ceil(len(items) / n)
    return [dict(items[i*chunk_size:(i+1)*chunk_size]) for i in range(n) if items[i*chunk_size:(i+1)*chunk_size]]


# Merge multiple JSON files into a single dict
def merge_json_files(file_paths: list[str]) -> dict:
    merged = {}
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            merged.update(data)
    return merged


def do_me(target_json: str, output_json: str):
    keys = read_json(target_json)
    # Load already translated keys if output_json exists
    existing_translations = {}
    if os.path.exists(output_json):
        try:
            with open(output_json, "r", encoding="utf-8") as existing_file:
                existing_translations = json.load(existing_file)
        except Exception:
            existing_translations = {}

    # Filter out already translated keys
    keys = {k: v for k, v in keys.items() if k not in existing_translations}
    if not keys:
        print(f"All keys in {target_json} already translated in {output_json}")
        write_log(f"All keys in {target_json} already translated in {output_json}")
        return

    # Open in r+ mode to append new entries
    with open(output_json, "r+", encoding="utf-8") as f:
        try:
            f.seek(0)
            existing_translations = json.load(f)
        except Exception:
            existing_translations = {}
            f.seek(0)
            f.truncate()
        # Seek to end for appending
        f.seek(0, os.SEEK_END)

        # If file is empty, write opening brace
        if os.path.getsize(output_json) == 0:
            f.write("{\n")
            first = True
        else:
            # Remove the last closing }
            f.seek(f.tell() - 2, os.SEEK_SET)
            f.truncate()
            f.write(",\n")
            first = False

        for key, value in keys.items():
            try:
                translation = random_translate(input_text=value, input_lang="en", output_lang="en", count=TRANSLATE_COUNT)
                print(f"Translated(file {target_json} -> {output_json}){key.ljust(30)}: {value} -> {translation}", end='\r', flush=True)
                write_log(f"Translated(file {target_json} -> {output_json}){key.ljust(30)}: {value} -> {translation}")
            except RuntimeError:
                print(f"Could not translate {key} in {target_json} , fallback is {value}")
                write_log(f"Could not translate {key} in {target_json} , fallback is {value}")
                translation = value  # fallback

            if not first:
                f.write(",\n")
            json_entry = json.dumps(key, ensure_ascii=False) + ": " + json.dumps(translation, ensure_ascii=False)
            f.write(json_entry)
            first = False
        f.write("\n}")
    print(f"Wrote translations incrementally to {output_json}")
    write_log(f"Wrote translations incrementally to {output_json}")



def main():
    input_path = FILE_INPUT
    source_dir = FILE_INPUT_CHUNK_DIR
    dist_dir = FILE_OUTPUT_CHUNK_DIR
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)

    data = read_json(input_path)
    num_chunks = min(16, len(data))
    chunks = split_dict(data, num_chunks)

    chunk_files = []
    dist_files = []
    for i, chunk in enumerate(chunks):
        source_file = os.path.join(source_dir, f"en_us_{i}.json")
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
        chunk_files.append(source_file)

        dist_file = os.path.join(dist_dir, f"gte_{i}.json")
        dist_files.append(dist_file)

    # Use ThreadPoolExecutor to parallelize do_me calls
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(do_me, chunk_files[i], dist_files[i]) for i in range(num_chunks)]
        for future in concurrent.futures.as_completed(futures):
            future.result()  # propagate exceptions if any

    merged = merge_json_files(dist_files)
    with open("gte.json", 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print("All chunks processed and merged.")
    write_log("All chunks processed and merged.")

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("exiting")