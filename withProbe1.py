# testing the "with" statement used for scope-based resource management. 
# Source: https://www.geeksforgeeks.org/with-statement-in-python/

# Run Command: python .\withProbe1.py 
import contextlib

# a simple file writer object
class MessageWriter(object):
    def __init__(self, file_name):
       self.file_name = file_name

    def __enter__(self):
        self.file = open(self.file_name, 'w')
        print("Opened the file...")
        return self.file

    def __exit__(self, *args):
       self.file.close()
       print("Closed the file...")

# using with statement with MessageWriter
with MessageWriter('my_file.txt') as xfile:
    xfile.write('hello world')
    print("wrote \"hello world\" to the file...")

         