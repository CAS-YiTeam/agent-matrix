import os
import pickle
import hashlib
from functools import wraps

def file_cache(cache_dir="cache"):
    def decorator(func):
        os.makedirs(cache_dir, exist_ok=True)  # Ensure cache directory exists

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique key based on the function name and the arguments
            hasher = hashlib.md5()
            key = (func.__name__, args, frozenset(kwargs.items()))
            key_string = str(args) + str(kwargs)
            hasher.update(key_string.encode('utf-8'))
            cache_filename = hasher.hexdigest() + '.cache'
            cache_filepath = os.path.join(cache_dir, cache_filename)

            # Try to load the cached result
            if os.path.exists(cache_filepath):
                try:
                    with open(cache_filepath, 'rb') as cache_file:
                        result = pickle.load(cache_file)
                        print("Returning cached result")
                        return result
                except (IOError, ValueError, EOFError, pickle.PickleError):
                    pass  # If cache reading fails, compute the result normally

            # Compute the result and cache it
            result = func(*args, **kwargs)
            with open(cache_filepath, 'wb') as cache_file:
                pickle.dump(result, cache_file)

            return result

        return wrapper
    return decorator

if __name__ == "__main__":
    # Example usage:
    @file_cache(cache_dir="my_cache")
    def compute(a, b, c=None):
        # Simulating a time-consuming or resource-intensive process
        import time
        time.sleep(2)
        return a * b * (c if c else 1)

    # Example call
    result = compute(2, 3, c=5)
    print(result)
    result = compute(2, 3, c=5)  # This call will be faster due to caching
    print(result)