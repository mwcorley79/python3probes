#  Sources: 
#     Very basic, first version port of Dr. Fawcett's Cpp11 BlockingQueue: 
#     Source: https://github.com/JimFawcett/CppBlockingQueue/tree/master/Cpp11-BlockingQueue

#  Other sources used for port: 
#    lists (as queues):                         https://www.geeksforgeeks.org/queue-in-python/
#    class definition/syntax:                   https://www.w3schools.com/python/python_classes.asp
#    Python Synchronization Primitives:         https://superfastpython.com/thread-condition/ 

# run (test) command: python .\pybq.py
import threading
import time;

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




# *** begin of BQueue test stub ***

# basic worker thread func, to handle/test the deQ operations 
def deQ_thread_function(bq):
    msg = bq.deQ()
    while msg != "quit":
        msg = bq.deQ()
        print(f'deQing: {msg} type: {type(msg)}')
        
        # sleep for thousandth of the second, to intentionally slow down the DeQer
        time.sleep(.0001)
    
def test_main():
    # construction is reference semantics (like C# and Java).  
    # test 1: strings 
    print("Test # 1: Blocking Queue of string (str) messages ")
    bq = BQueue()  
    #  spawn deQ worker thread
    t = threading.Thread(target=deQ_thread_function, args=(bq,))
    t.start()

    #  using primary thread for enQ process, for 15 message count test
    for i in range(15):
        msg = "msg #:" + str(i+1) 
        bq.enQ(msg)
        print(f'main enQing: {msg}');
       
    # signal the deQer thread, we are done "quit" message
    bq.enQ("quit")
    
    # wait for deQer worker thread to exit
    t.join()  
    print("Test # 1: complete\n")

    print("Test # 2: Blocking Queue of integer (int) messages ")
    # testing queue 2: integers 
    bq2 = BQueue() 
    #  spawn deQ worker thread
    t = threading.Thread(target=deQ_thread_function, args=(bq2,))
    t.start()

    #  using primary thread for enQ process, for 10 message count test
    for i in range(10):
        msg = (i+1) 
        bq2.enQ(msg)
        print(f'main enQing: {msg}');
       
   
    # signal the deQer thread, we are done "quit" message
    bq2.enQ("quit")
    
    # wait for deQer worker thread to exit
    t.join()  
    print("Test # 2: complete")


if __name__ == "__main__":
    test_main()

