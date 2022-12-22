import pybq as BlockingQueue
import asyncio
import threading
import time

def deQ_thread_function(bq):
  
    msg = bq.deQ()
    while msg != "quit":
        print(f'Thread deQued: {msg} -> type: {type(msg)}')
        msg = bq.deQ()
        time.sleep(.0001)
       
def main():
    # construction based refernce semantics (like C# and Java).  
    # test 1: strings 
    bq = BlockingQueue.BQueue() 
    
    #  spawn deQ worker thread
    t = threading.Thread(target=deQ_thread_function, args=(bq,))
    t.start()

    #  using primary thread for enQ process
    for i in range(10):
        msg = "msg #:" + str(i+1) 
        bq.enQ(msg)
        print(f'main enQing: {msg}');
       
    bq.enQ("quit")
    t.join()


    # testing queue 2: ints
    bq2 = BlockingQueue.BQueue() 
    
    #  spawn deQ worker thread
    t = threading.Thread(target=deQ_thread_function, args=(bq2,))
    t.start()

    #  using primary thread for enQ process
    for i in range(10):
        msg = (i+1) 
        bq2.enQ(msg)
        print(f'main enQing: {msg}');
       
    bq2.enQ("quit")
    t.join()


if __name__ == "__main__":
    main()

