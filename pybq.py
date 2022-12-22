#  Sources: 
#     Very basic, first version port of Dr. Fawcett's Cpp11 BlockingQueue: 
#     https://github.com/JimFawcett/CppBlockingQueue/tree/master/Cpp11-BlockingQueue

#  Other sources: 
#    lists (as queues):                         https://www.geeksforgeeks.org/queue-in-python/
#    class definition/syntax:                   https://www.w3schools.com/python/python_classes.asp
#    Python Synchronization Primitives:         https://superfastpython.com/thread-condition/ 

import threading

class BQueue:
    def __init__(self):
         self.q = [] # using a list, since Python does not have Queues as built-in collection
         self.lock = threading.Lock()
         self.cond = threading.Condition(self.lock)
      

    def enQ(self, message):
        with self.cond:
            self.q.append(message)
            self.cond.notify(1)
     
    def deQ(self):      
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

    def size(self):
        with self.cond:
            return len(self.q)
