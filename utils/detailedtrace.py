import traceback


def getDetailed(e: Exception) -> str:
    try:
        raise e
    except Exception as e:
        # Create a traceback from the error
        tb = "".join(traceback.format_exception(e, e, e.__traceback__))  # type: ignore

        return tb
