#  Sources: 
#     2nd version port of Dr. Fawcett's Cpp11 BlockingQueue, but experimenting with Python Generics 
#     https://github.com/JimFawcett/CppBlockingQueue/tree/master/Cpp11-BlockingQueue

#  Other sources: 
#    lists (as queues):                         https://www.geeksforgeeks.org/queue-in-python/
#    class definition/syntax:                   https://www.w3schools.com/python/python_classes.asp
#    Python Synchronization Primitives:         https://superfastpython.com/thread-condition/ 
#    Generics Source:                          https://medium.com/@steveYeah/using-generics-in-python-99010e5056eb

# run (test) command: python .\pybqGeneric.py

import threading
from typing import Generic, List, TypeVar
import time

# extending the Generic base class, and by defining the generic 
# types we want to be valid within this class. In this case we define T
T = TypeVar("T")

# limit the types that can be represented by a generic type
# similar to constraints in C#
#T = TypeVar("T", str, int) # T can only represent types of int and str

class BQueue(Generic[T]):
    def __init__(self) -> None:
         self.q: List[T] = [] # using a list, since Python does not have Queues as built-in collection
         self.lock = threading.Lock()
         self.cond = threading.Condition(self.lock)
      

    def enQ(self, message: T) -> None:
        with self.cond:
            self.q.append(message)
            self.cond.notify(1)
     
    def deQ(self) -> T:      
         with self.cond:
            if len(self.q) > 0:
               # deque from the front
               temp_msg = self.q.pop(0)
               return temp_msg

            # may have spurious returns so loop on !condition
            while len(self.q) == 0: 
                self.cond.wait_for(lambda: len(self.q) > 0)

            # deque from the front
            temp_msg = self.q.pop(0)
            return temp_msg

    def size(self) -> int:
        with self.cond:
            return len(self.q)


# *** begin of BQueue test stub ***
# basic worker thread func, to handle/test the deQ operations 

def deQ_thread_function(bq):
    msg = bq.deQ()
    while msg != "quit":
        msg = bq.deQ()
        print(f'deQing: {msg} type: {type(msg)}')
        time.sleep(.0001)
       

def main_test():
    print("*** Testing Generics ***")
    # construction is reference semantics (like C# and Java).  
    # test 1: strings 
    bq = BQueue[str]()  # declare Generic BQ with string type
    
    #  spawn deQ worker thread
    t = threading.Thread(target=deQ_thread_function, args=(bq,))
    t.start()

    #  using primary thread for enQ process
    for i in range(10):
        msg = "msg #:" + str(i+1) 
        bq.enQ(msg)
        print(f'main enQing: {msg}')
       
    bq.enQ("quit")
    t.join()


    # testing queue 2: ints
    bq2 = BQueue[int]() # declare Generic BQ with int type
    #  spawn deQ worker thread
    t = threading.Thread(target=deQ_thread_function, args=(bq2,))
    t.start()

    #  using primary thread for enQ process
    for i in range(10):
        msg = (i+1) 
        bq2.enQ(msg)
        print(f'main enQing: {msg}')
       
    bq2.enQ("quit")
    t.join()
   


if __name__ == "__main__":
    main_test()
