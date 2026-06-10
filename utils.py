def normalize_text(name):
    name = name.lower().strip()
    name_arr = name.split(' ')
    name = " ".join(name_arr)

    return name