import os

output_file = os.path.join(os.getcwd(), "directory_structure.txt")


def write_to_file(content):
    """Write content to a file, creating directories if necessary."""
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(content)


def print_directory_structure(root_dir, prefix='', exclude=None, suffixes_to_ignore=('.xlsx', '.csv')):
    if exclude is None:
        exclude = []
    files = sorted(os.listdir(root_dir), key=lambda x: (
        not os.path.isdir(os.path.join(root_dir, x)), x.lower()))
    count = len(files)
    for index, file in enumerate(files):
        path = os.path.join(root_dir, file)
        # Skip directories if they are in the exclusion list
        if os.path.isdir(path) and file in exclude or file.endswith(suffixes_to_ignore):
            continue
        connector = "└── " if index == count - 1 else "├── "
        s = prefix + connector + file
        print(s)
        write_to_file(s + "\n")
        if os.path.isdir(path):
            extension = "    " if index == count - 1 else "│   "
            print_directory_structure(path, prefix + extension, exclude)


def main():
    # Hard-coded settings
    directory_to_list = os.getcwd()  # Change this to your desired directory
    exclude_dirs = ["__pycache__", ".git", ".venv",
                    ".vscode", "local_tests", "results", ".pytest_cache", "dist", "build"]

    print(f"Directory structure for: {directory_to_list}\n")
    print_directory_structure(directory_to_list, exclude=exclude_dirs)


if __name__ == '__main__':
    main()
