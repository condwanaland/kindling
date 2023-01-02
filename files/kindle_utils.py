def write_file(path: str, files: list) -> None:
    with open(path, 'w') as fp:
        for item in files:
            # write each item on a new line
            fp.write("%s\n" % item)


def read_file(file: str) -> list[str]:
    with open(file) as f:
        contents = f.readlines()
        return contents
