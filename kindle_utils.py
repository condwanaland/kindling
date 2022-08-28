def write_file(path: str, files: list):
    with open(path, 'w') as fp:
        for item in files:
            # write each item on a new line
            fp.write("%s\n" % item)


def read_file(file: str):
    with open(file) as f:
        contents = f.readlines()
        return contents
