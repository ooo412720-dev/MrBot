from app.core.roles import Role


def promote_user(
    user,
    role
):

    user.role = role

    return user