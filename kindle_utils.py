def write_file(path: str, files: list):
    with open(path, 'w') as fp:
        for item in files:
            # write each item on a new line
            fp.write("%s\n" % item)


def read_file(file: str):
    with open(file) as f:
        contents = f.readlines()
        return contents


def process_list(new_books: list):
    converted_list = []
    for element in new_books:
        converted_list.append(element.strip())

    stripped_list = [x for x in converted_list if x]

    return stripped_list
