import os
import sys
import json
import re
import argparse
from cson_parser import parse_cson


def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert Boostnote notes to Obsidian format')
    parser.add_argument('input_dir', help='Directory containing Boostnote .cson files')
    parser.add_argument('output_dir', help='Directory where Obsidian notes will be saved')
    parser.add_argument('--boostnote-json', help='Path to boostnote.json file (default: parent directory of input_dir)')
    return parser.parse_args()


# iterate over files in specified directory and filter by predicate
def gen_filenames(directory, predicate):
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        # check if it is a file and predicate is true
        if os.path.isfile(file_path) and predicate(file_path):
            yield file_path


def cson_extension_predicate(file_path):
    file_extension = os.path.splitext(file_path)[1]
    return file_extension == ".cson"


def clean_name(name: str) -> str:
    # Trim the string and then remove any characters except:
    # - Hyphen (-)  Dot (.) Space ( )
    # - Word characters (letters, digits, and underscore)
    return re.sub(r"(?u)[^-\w. ]", "", str(name).strip())


def trim_and_replace(input_str: str) -> str:
    # First, remove leading and trailing spaces:
    trimmed = input_str.strip()
    # Then, replace all inner whitespace (including spaces, tabs, etc.) with an underscore:
    result = re.sub(r'\s+', '_', trimmed)
    return result


def is_valid_obsidian_tag(tag: str) -> bool:
    """
    Check if the tag is a valid Obsidian tag.
    https://help.obsidian.md/tags

    Requirements:
      - The tag is not empty.
      - The tag contains only alphabetical letters, digits, underscores (_),
        hyphens (-), and forward slashes (/).
      - The tag must include at least one character that is not a digit.
    """
    if not tag:
        return False

    # Regex breakdown:
    #   ^                  : start of the string.
    #   (?=.*[^0-9])      : positive lookahead to require at least one non-digit.
    #   [A-Za-z0-9_/-]+    : one or more allowed characters (letters, digits, underscore, hyphen, forward slash).
    #   $                  : end of the string.
    pattern = r'^(?=.*[^0-9])[A-Za-z0-9_/-]+$'
    return bool(re.fullmatch(pattern, tag))


def generate_tags(tags_input):
    if tags_input:
        tags = []

        for tag in tags_input:
            tag_no_whitespace = trim_and_replace(tag)
            if is_valid_obsidian_tag(tag_no_whitespace):
                tags.append(tag_no_whitespace)

        tags_text = '#' + " #".join(tags) + os.linesep
    else:
        tags_text = ""
    return tags_text


# boostnote saves all notes in one folder, files might contain multiple sub-files(snippets)
# and all folders are just IDs, the actual fodler names are in the boostnote.json file.
def convert_to_fs_structure(parsed_file: dict, output_path: str, folder_names: dict):
    # 'MARKDOWN_NOTE'
    # type folder tags title content updatedAt
    # 'SNIPPET_NOTE'
    # description snippets
    #   list of dicts name mode(c++) content
    folder = folder_names[parsed_file['folder']]['name']
    tags_text = generate_tags(parsed_file['tags'])

    title = parsed_file['title']
    file_name = title.split()[0:5]

    if parsed_file['type'] == 'MARKDOWN_NOTE':
        if not parsed_file['content']:
            print(f"Empty content: {parsed_file}")
            return

        content = tags_text + parsed_file['content']

        file_path = os.path.join(output_path, folder, clean_name(file_name) + '.md')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(content)
            print(f"Created  file {file_path}.")

    elif parsed_file['type'] == 'SNIPPET_NOTE':
        description = '# ' + parsed_file['description'].strip() + os.linesep
        snippets = parsed_file['snippets']

        for snippet in snippets:
            if not snippet['content']:
                print(f"Empty content: {parsed_file}")
                return

            name = snippet['name']
            file_path = os.path.join(output_path, folder, clean_name(file_name), name + '.md')
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            mode = snippet['mode']
            code_block_start = "```" + mode
            code_block_end = "```"
            content = description + code_block_start + snippet['content'] + code_block_end

            with open(file_path, 'w', encoding='utf-8') as new_file:
                new_file.write(content)
            print(f"Created  file {file_path}.")


if __name__ == "__main__":
    args = parse_arguments()
    
    in_directory = args.input_dir
    out_directory = args.output_dir
    boostnote_json_file_path = args.boostnote_json or os.path.join(os.path.dirname(in_directory), "boostnote.json")

    print(f"Input directory: {in_directory}")
    print(f"Output directory: {out_directory}")
    print(f"Boostnote JSON file: {boostnote_json_file_path}")

    boostnote_directories = {}
    with open(boostnote_json_file_path, 'r', encoding="utf8") as file:
        data = json.load(file)
        boostnote_directories = {obj['key']: obj for obj in data["folders"]}

    print(f"Found {len(boostnote_directories)} folders in boostnote.json")

    for filename in gen_filenames(in_directory, cson_extension_predicate):
        print(f"Processing file: {filename}")
        with open(filename, "r", encoding='utf8') as cson_file:
            text = cson_file.read()
            if len(text) == 0:
                print("File is empty!")
            parsed_text = parse_cson(text)
            convert_to_fs_structure(parsed_text, out_directory, boostnote_directories)

            # debugging code to print the generated tokens.
            #for key, value in parse_cson(text).items():
            #    print(f"key: {key}  type: {type(value)}")
            #    if isinstance(value, str):
            #        print(f"value: {value[:30]}")
            #    else:
            #        print(f"value: {value}")
