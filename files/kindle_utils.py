def write_file(path: str, files: list) -> None:
    with open(path, "w") as file:
        for item in files:
            file.write(f"{item}\n")


def read_file(file: str) -> list[str]:
    with open(file) as contents:
        return [line.rstrip("\r\n") for line in contents]
