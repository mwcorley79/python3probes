# Mike C.  Python 3, destructior test.  Muck like finalizer in C#, but very different than
# C++ since the Python and C# object models are based reference semantics, 
# while C++ is based value semantics  

# derviced from source: https://www.geeksforgeeks.org/destructors-in-python/?ref=lbp

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
print("""Note: if emp2 is deleted excplicity (the above line), you'll see the 
          destructor announced before this message, other is the referense is deleted
          when object goes out scope... and tnhe you'll see announce after this message """);
#emp 1 is now deleted, because it goes of out scope


 