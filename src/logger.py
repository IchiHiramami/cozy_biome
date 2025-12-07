
def log(timestamp : str, type : int, message: str):
    """
    Interaction Logger

    Type numbering:
    1 - WARNING
    2 - INFO
    3 - ADMIN ACCESS
    4 - OTHERS
    """
    match type:
        case 1:
            declaration = "WARNING"
        case 2:
            declaration = "INFO"
        case 3:
            declaration = "ADMIN ACCESS"
        case _:
            declaration = "OTHERS"
        
    print(f"{timestamp} -- {declaration} -- {message}")