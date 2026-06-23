BAD_NAMES = [

    "admin",
    "owner",
    "telegram"
]
def bad_name(
    name
):

    lowered = name.lower()

    return any(
        x in lowered
        for x in BAD_NAMES
    )