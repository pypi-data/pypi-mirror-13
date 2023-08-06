def get_protocol_from_int(id):
    return {
        0: "ftp",
        1: "fs",
        2: "smb",
        3: "sftp",
        4: "http",
        5: "https"}[id]


def get_protocol_id_from_name(name):
    return {
        "ftp": 0,
        "fs": 1,
        "smb": 2,
        "sftp": 3,
        "http": 4,
        "https": 5
    }[name.lower()]