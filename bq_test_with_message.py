# testing  the blocking queue class (pybq.py), together with the Message class (Message.py) 
# importing blocking and message 

# Run (test) command: python .\bq_test_with_message.py



import pybq as BlockingQueue
from Message import *

import threading
import time

# basic worker thread func, to handle/test the deQ operations 
def deQ_thread_function(bq):
    msg = bq.deQ()
    while msg.msg_type  != MessageType.END: 
        msg = bq.deQ()
        print(f'deQing: {msg} object type: {type(msg)}')
        print(f"\"msg\" identity      : {id(msg)}")
        print(f"\"msg\" data          : {msg}")
        print(f"\"msg\" len           : {msg.content_len}")
        print(f"\"msg\" type          : {msg.msg_type}")
        print(f"\"msg content (str)   : {msg.to_string()} {type(msg.to_string())}")
        print(f"\"msg content (bytes) : {msg.content} {type(msg.content)}\n")
        # time.sleep(.000001)


if __name__ == "__main__":
    # instantiate the blocking queue
    bq = BlockingQueue.BQueue() 
    
    #  spawn deQ worker thread
    t = threading.Thread(target=deQ_thread_function, args=(bq,))
    t.start()

    #  using primary thread for enQ process
    for i in range(10):
        
        # construct a string message 
        msg = Message("msg #:" + str(i+1), MessageType.STRING)
       
        bq.enQ(msg)
        print(f'main enQing: {msg}');
       
    bq.enQ(Message.empty_init(MessageType.END))
    t.join()
    

