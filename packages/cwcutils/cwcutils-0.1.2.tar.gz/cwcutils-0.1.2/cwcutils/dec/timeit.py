def timeit(func):
    import time

    def wrapper(*args):

        a = time.time()

        res =  func(*args)

        b = time.time()
        elapsed_ms = (b-a)*1000
        print('%f ms\n'% elapsed_ms)

        return res

    return wrapper
