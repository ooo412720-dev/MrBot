AUTO_REPLIES = {

    "السلام عليكم":
    "وعليكم السلام",

    "ping":
    "pong"
}
def auto_reply(
    text
):

    return AUTO_REPLIES.get(
        text
    )