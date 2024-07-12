from sys import stdin, stdout, stderr

class Stream:
    # TODO: kwargs for file opening
    def __init__(self, action_or_filename: str, mode: str = None) -> None:
        self.action_or_filename = action_or_filename
        self.mode = mode
        
        self.keywords = {
            "stdin": stdin,
            "stdout": stdout,
            "stderr": stderr
        }
    
    def __enter__(self):
        if self.action_or_filename in self.keywords:
            self.handle = self.keywords[self.action_or_filename]
        else:
            # assume it's a file name -> mode must not be None
            assert self.mode
            self.handle = open(self.action_or_filename, self.mode, encoding='utf-8')
        return self.handle
    
    def __exit__(self, *args):
        self.handle.close()

def flatten ( array: list) -> list:
    return [ item for sublist in array for item in sublist ]

def split_into_chunks(_in: list, chunk_size: int) -> list:
    return [ _in [ i : i + chunk_size ] for i in range(0, len(_in), chunk_size) ]
