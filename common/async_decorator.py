from threading import Thread


def decorator(func):
    def threads(*args, **kwargs):
        t = Thread(target=func, args=args, **kwargs)
        t.start()
    return threads
