def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except IOError:
        print(f"An error occurred while reading the file at {file_path}.")