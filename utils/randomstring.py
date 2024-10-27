import random, string


def randomword(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))
