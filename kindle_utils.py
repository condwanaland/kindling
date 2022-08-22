def write_file(working_dir: str, files: list, filename: str = "book_list.txt"):
    with open(working_dir + filename, 'w') as fp:
        for item in files:
            # write each item on a new line
            fp.write(item)


def read_file(file: str):
    with open(file) as f:
        contents = f.readlines()
        return contents
