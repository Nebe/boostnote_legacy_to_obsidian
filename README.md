# CSON Parser

A simple Python parser for CSON (CoffeeScript Object Notation) format, primarily designed for converting legacy Boostnote notes to Obsidian format.

## Quick Start

### Converting Boostnote Notes to Obsidian

To convert your Boostnote notes to Obsidian format:

```bash
python boostnote_to_obsidian.py <input_directory> <output_directory> [--boostnote-json BOOSTNOTE_JSON]
```

Arguments:
- `input_directory`: Path to your Boostnote notes directory (required)
- `output_directory`: Where to save the converted Obsidian notes (required)
- `--boostnote-json BOOSTNOTE_JSON`: Path to boostnote.json file (optional, defaults to parent directory of input_directory)

Examples:
```bash
# Basic conversion
python boostnote_to_obsidian.py ./boostnote_notes ./obsidian_vault

# Specify boostnote.json location
python boostnote_to_obsidian.py ./boostnote_notes ./obsidian_vault --boostnote-json ./config/boostnote.json
```

The script will:
- Convert all `.cson` files in the input directory
- Create corresponding markdown files in the output directory
- Preserve the folder structure using information from boostnote.json
- Convert tags and metadata to Obsidian format

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/cson_parser.git
cd cson_parser
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Description

This project provides a lightweight CSON parser implementation that focuses on the specific needs of converting Boostnote notes to Obsidian format. While it doesn't support the full CSON specification, it handles the essential features needed for this conversion task.

## Features

- Parses CSON format into Python dictionaries
- Supports basic CSON syntax including:
  - Strings (single and multi-line)
  - Numbers
  - Booleans
  - Lists
  - Dictionaries
  - Nested structures

## Limitations

The parser has several limitations that users should be aware of:

1. **String Handling**:
   - String literals separated by whitespace are not connected into one string
   - Verbatim strings (delimited by "|" and new line) are not supported
   - Strings must be properly quoted with either `"` or `'''`

2. **Key-Value Pairs**:
   - Only supports `:` as key-value separator
   - The alternative `=` separator is not supported
   - Keys must be unquoted identifiers

3. **Lists**:
   - List items must be separated by newlines, not commas
   - Each list item must be on its own line
   - JSON-style comma-separated lists are not supported

4. **JSON Compatibility**:
   - JSON syntax is not supported, particularly:
     - Comma-separated values
     - JSON-style object notation
     - JSON-style array notation

5. **Nesting**:
   - Nested structures must use explicit braces `{}` for dictionaries
   - Indentation-based nesting is not supported
   - All nested structures must be properly delimited

## Advanced Usage

### Basic CSON Parsing

```python
from cson_parser import parse_cson

# Parse CSON string
cson_string = '''
title: "My Note"
content: "This is a note"
tags: [
    "important"
    "work"
]
'''
result = parse_cson(cson_string)
print(result)
```

## Project Structure

- `cson_parser.py` - Main parser implementation
- `boostnote_to_obsidian.py` - Utility for converting Boostnote notes to Obsidian format
- `tests/` - Test cases for the parser

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 