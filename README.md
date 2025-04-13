# Boostnote to Obsidian Converter

A tool for converting your Boostnote notes to Obsidian format. This project includes a lightweight CSON parser specifically designed to handle Boostnote's note format.

If you have any issues or want to improve it - create a github issue for it and I will gladly take a look at it. See limitations below.

## Quick Start

### Converting Legacy Boostnote Notes to Obsidian

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

This project helps you migrate your notes from Boostnote to Obsidian. It includes a specialized CSON parser that handles Boostnote's specific note format, converting your notes while preserving their structure, tags, and metadata.

## Features

- Converts Boostnote `.cson` files to Obsidian markdown format
- Preserves folder structure using information from boostnote.json
- Maintains tags and metadata in Obsidian-compatible format
- Handles Boostnote-specific CSON syntax including:
  - Strings (single and multi-line)
  - Numbers
  - Booleans
  - Lists
  - Dictionaries
  - Nested structures

## Limitations

### Parser Limitations

The CSON parser has several limitations that users should be aware of:

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

### Converter Limitations

The Boostnote to Obsidian conversion process has the following limitations:

1. **Attachments and Links**:
   - No automatic detection or conversion of attachments
   - Internal links between notes are not preserved
   - Contributions implementing these features are welcome!

## Project Structure

- `boostnote_to_obsidian.py` - Main conversion script
- `cson_parser.py` - Supporting CSON parser implementation
- `tests/` - Test cases for the CSON parser

## Contributing

Contributions are welcome! We're particularly interested in submissions that add support for:
- Attachment detection and conversion
- Internal link preservation
- Other Boostnote-specific features

Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 