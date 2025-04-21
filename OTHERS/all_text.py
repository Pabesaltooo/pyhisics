import os

def read_py_files(directory):
    all_text = ""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "all_text.py":
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_text += f"--- {file_path} ---\n"
                    all_text += f.read() + "\n\n"
    return all_text

def main():
    directory = os.path.dirname(os.path.abspath(__file__))
    all_text = read_py_files(directory)
    output_file = os.path.join(directory, "all_text_output.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(all_text)

if __name__ == "__main__":
    main()