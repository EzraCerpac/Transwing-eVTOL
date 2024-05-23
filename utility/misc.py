import inspect


def get_caller_file_name(n_back: int = 2, n_dirs: int = 1) -> str:
    """
    Returns the name of the file from which the current function is called.
    """
    # Get the previous frame in the stack, i.e. the calling function
    frame = inspect.currentframe().f_back
    for _ in range(n_back):
        frame = frame.f_back

    # Get the file name of the calling function
    file_name = frame.f_globals["__file__"]
    if 'plot_functions' in file_name:
        file_name = frame.f_back.f_globals["__file__"]


    last_slash = file_name.rfind("/")
    for _ in range(n_dirs):
        last_slash = file_name.rfind("/", 0, last_slash)
    file_name = file_name[last_slash + 1:].replace('.py', '')

    return file_name
