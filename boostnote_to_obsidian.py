import os
import sys
from cson_parser import parse_cson


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


if __name__ == "__main__":
    # second argument is expected to be the directory path to the boostnote notes
    in_directory = sys.argv[1]

    out_directory = sys.argv[2] if len(sys.argv) == 3 else os.path.join(in_directory, "output")

    for filename in gen_filenames(in_directory, cson_extension_predicate):
        print(filename)
        with open(filename, "r", encoding='utf8') as cson_file:
            text = cson_file.read()
            if len(text) == 0:
                print("File is empty!")
            parsed_text = parse_cson(text)
            for key, value in parse_cson(text).items():
                print(f"key: {key}  type: {type(value)}")
                if isinstance(value, str):
                    print(f"value: {value[:30]}")
                else:
                    print(f"value: {value}")
