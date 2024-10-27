from revolt import SendableEmbed


def error(description: str | None = None, error: str | None = None) -> SendableEmbed:

    description = (
        description
        or "An error occurred while running the command. Please try again later."
    )

    if error is None:
        return SendableEmbed(
            title="Uh oh! Something went wrong.",
            description=description,
        )

    return SendableEmbed(
        title="Uh oh! Something went wrong.",
        description=f"""{description}

        **Error:**
        {error}""",
    )
