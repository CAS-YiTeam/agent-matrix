

def verify_deps():
    try:
        import numpy
    except ImportError:
        raise ImportError("numpy is not installed. Please install it by running: pip install numpy")
