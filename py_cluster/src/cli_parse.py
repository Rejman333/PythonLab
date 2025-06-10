import argparse

def _threshold_type(value: str) ->int:
    """
       Validate and convert threshold argument to an integer between 0 and 255.

       Args:
           value (str): Input value from the command line.

       Returns:
           int: Validated threshold value.

       Raises:
           argparse.ArgumentTypeError: If the value is not within 0–255.
       """

    ivalue = int(value)
    if ivalue < 0 or ivalue > 255:
        raise argparse.ArgumentTypeError("threshold must be between 0 and 255")
    return ivalue

def _gray_type(value: str) -> int:
    """
     Convert grayscale argument to an internal index.

     Accepts either an integer (0–3) or a string ('r', 'g', 'b', 'm') corresponding to color channels.

     Args:
         value (str): Input value from the command line.

     Returns:
         int: Index corresponding to the grayscale mode.

     Raises:
         argparse.ArgumentTypeError: If the input is invalid.
     """
    valid_list = ['r', 'g', 'b', 'm']
    try:
        ivalue = int(value)
        if 0 <= ivalue <= 3:
            return ivalue
    except ValueError:
        if value.lower() in valid_list:
            return valid_list.index(value.lower())
    raise argparse.ArgumentTypeError("gray must be an int (0–3) or one of: r, g, b, m")

def prepare_cli()-> argparse.Namespace:
    """
        Parse command-line arguments for the Py Cluster tool.

        Returns:
            argparse.Namespace: Parsed arguments including:
                - filename (str): Input image file.
                - threshold (int): Threshold for binarization.
                - gray (int): Grayscale mode index.
                - debug (bool): Flag to enable debug mode.
        """
    parser = argparse.ArgumentParser(description="My CLI tool")
    parser.add_argument("filename",
                        help="Input file name")
    parser.add_argument("-t", "--threshold", type=_threshold_type, default=127,
                        help="Threshold value (0–255) used for binary image thresholding (default: 128)")
    parser.add_argument("-g", "--gray", type=_gray_type, default="m",
                        help="Grayscale mode: 0=red, 1=green, 2=blue, 3=mean, or use r/g/b/m (default: 3)")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug mode")

    return parser.parse_args()