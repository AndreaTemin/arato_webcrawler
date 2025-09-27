from time import time

def save_page(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def function_timer(function):
    def inner(*args, **kwargs):
        now = time()
        function(*args, **kwargs)
        diff = time() - now
        
        print(f"\nTime - {function.__name__} took {diff} to exectute " )
    return inner
