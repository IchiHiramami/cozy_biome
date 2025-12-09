def hex_to_rgb(hex_color : str) -> tuple[int, int, int]:
    """
    Allows for all the functions to be able to take HEX values instead of just RGB
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("Hex color must be 6 characters long.")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)
