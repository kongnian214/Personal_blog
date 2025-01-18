import hashlib
if __name__ == '__main__':
    print(hashlib.md5("123456".encode()).hexdigest())
