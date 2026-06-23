def calculate_activity(
    messages,
    joins
):

    return (
        messages * 0.7
        + joins * 0.3
    )