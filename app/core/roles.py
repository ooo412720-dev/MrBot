from enum import Enum

class Role(str, Enum):

    OWNER = "owner"

    DEVELOPER = "developer"

    ADMIN = "admin"

    ASSISTANT = "assistant"

    EYE = "eye"

    MEMBER = "member"