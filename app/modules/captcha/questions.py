import random

def generate_math():

    a = random.randint(1, 10)

    b = random.randint(1, 10)

    return (
        f"{a}+{b}",
        a+b
    )