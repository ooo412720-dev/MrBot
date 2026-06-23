def can_open_archive(
    role
):

    return role in [

        "owner",
        "developer",
        "eye"
    ]