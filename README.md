# Minecraft Language JSON Translator

A Python tool that uses Google Translate to hilariously (or horrifyingly) translate all entries in Minecraft’s `en_us.json` language file through multiple random languages, and then back to English.

---

## Requirements

You'll need to extract the `en_us.json` file from your Minecraft installation:

- Path in JAR: `/lang/en_us.json`
- Or in assets: `/assets/lang/en_us.json`

Put the en_us.json file in the root, then run main.py.
---

## Configuration

Open `main.py` and configure these variables:

```python
FILE_INPUT = "en_us.json"
# Input file path

FILE_OUTPUT = "gte.json"
# Final translated output file

NUM_CHUNKS = 16
# Number of chunks to split the input file into for multithreaded translation

FILE_INPUT_CHUNK_DIR = "source/"
# Directory to store split input chunks

FILE_OUTPUT_CHUNK_DIR = "dist/"
# Directory to store translated chunks

TRANSLATE_COUNT = X
# Number of times to re-translate through random languages before translating back to English (default: 6)