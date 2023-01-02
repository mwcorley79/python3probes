# Python 3, destructior test.  Much like finalizer in C#, but very different than
# C++ since the Python and C# object models use reference semantics, 
# and C++ uses value semantics  

# derived from source: https://www.geeksforgeeks.org/destructors-in-python/?ref=lbp

# Run Command: python .\destructor_probe.py

class Employee:
    # Initializing
    def __init__(self):
        print('Employee created.')

    # Deleting (Calling destructor)
    def __del__(self):
        print('*** Destructor called, Employee deleted ***')

emp1 = Employee()
emp2 = emp1  

del emp1; # explicity delete emp1 reference

print("Deleting emp1 explicity...not destructor is called becuase emp2 is reference to emp1")
# del emp2  # uncomment to test destructor 

print("""Note: if emp2 is deleted excplicity (line 24 above), you'll see the 
          destructor announced before this message, otherwise the referense is deleted
          when object goes out scope... and the you'll see the destructor announced after this message """);
#emp 1 is now deleted, because it goes of out scope


 