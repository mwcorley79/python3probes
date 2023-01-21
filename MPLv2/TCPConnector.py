import socket
import pybq as BlockingQueue
import time
import threading
from EndPoint import EndPoint
from Message import *
import time

class TCpConnector:
    def __init__(self):   
        self._sendQ = BlockingQueue.BQueue()
        self._recvQ = BlockingQueue.BQueue()
        
        self.is_receiving = False
        self.is_sending = False

        self.use_recv_q = True
        self.use_send_q = True
    
        self._is_connected = False
     
    def UseQueues(self, val):
        self.use_send_q = val
        self.use_recv_q = val

    def is_connected(self):
        return self._is_connected

    def connect(self, ep):
        ''' make single attempt to connect to server at endpoint ep'''
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect( (ep.ip, ep.port))
        self._is_connected = True
        self._start()

    def connectpersist(self, ep, retries, wtime_secs, vlevel=1):
        '''make retries attempts to connect to server at endpoint ep'''
        runAttempts = 0
        while runAttempts < retries:
            try:
              runAttempts +=1
              if vlevel > 0:
                 print(f"Connection Attempt # {runAttempts} of {retries} to {ep}")
              self.connect(ep)
              break
            except:
               if vlevel > 0:
                  print(f"Failed Attempt # {runAttempts}")
               time.sleep(1)
           
        return runAttempts
 
    def postmessage(self, msg): 
        ''' post a message into the send blocking queue'''
        self._sendQ.enQ(msg)

    def sendsessage(self, msg):
        ''' send the message directly over the socket, bypassing the send blocking queue'''
        self._sendsocketmessage(msg)


    def _start(self):
        '''if a valid TCP connection to server exists, that start the send/recv worker threads'''
        if self.is_connected():
            if self.use_send_q:
                self._startsending()

            if self.use_recv_q:
               self._start_receiving()

    def _startsending(self):
        ''' start dedicated worker thread: sendproc to handling sending message over the socket'''
        if self.is_sending == False:
            self.is_sending = True
            self._sendthread = threading.Thread(target=self._sendproc)
            self._sendthread.start()

    def _stopsending(self):
        '''cause dedicated worker thread: sendproc to shutdown: by enQing STOP_SENDING message '''
        try:
          if self.is_sending:
             self.postmessage(Message.empty_init(MessageType.STOP_SENDING))
             self._sendthread.join()
             self.is_sending = False
        except:
             self.is_sending = False

    def _sendproc(self):
        ''' dedicated worker thread to serialize messages into the socket '''
        msg = self._sendQ.deQ()
        while msg.msg_type != MessageType.STOP_SENDING:
            self._sendsocketmessage(msg)
            msg = self._sendQ.deQ()

    
    def _sendsocketmessage(self, msg):
        '''send messsage into the socket '''
        self._sock.sendall(msg.get_serialized_message)

    def _start_receiving(self):
        if not self.is_receiving:
            self.is_receiving = True
            self._recv_thread = threading.Thread(target=self._recv_proc)
            self._recv_thread.start()

    def _stop_receiving(self):
        try:
          if self.is_receiving:
             self._recv_thread.join()
             self.is_receiving = False
        except:
            self.is_receiving = False

    def get_message(self):
        return self._recvQ.deQ()
        
    def recv_message(self):
        return self._receive_socket_message()

    def _recv_proc(self):
        try:
            # receive msg from the socket
            msg = self._receive_socket_message()

            # if not the DISCONNECT signal, then copy (reference) into the receive blocking queue
            while msg.msg_type != MessageType.DISCONNECT:
               self._recvQ.enQ(msg)
               msg =  self._receive_socket_message()
            
            #lastly, enQ the DISCONNECT message (needed to shutdown app_proc)
            self._recvQ.enQ(msg)
        except Exception as e: 
            print(f'Error in TCPConnector::_recv_proc(): {e}')


    def _receive_socket_message(self):
         # receive the fixed size message header (see wire protocol in Message.py)
         hdr_bytes = self._recvall(self._sock, PackedMessage.hdr_len())
         readLen = len(hdr_bytes)

         if readLen == PackedMessage.hdr_len():
            # extract message hdr attributes, message type, and content length to read out the socket
            header_vals = PackedMessage.extract_message_attribs(hdr_bytes)
            msg_type  = MessageType(header_vals[0])
            content_len = header_vals[1]
            
            # recv message data
            content = self._recvall(self._sock, content_len)
            if len(content) != content_len:
                raise socket.error()
            return Message(content, msg_type)

         # zero length message, sent to signal close, results in a disconnect being queued
         if readLen == 0:
            return Message.empty_init(MessageType.DISCONNECT)
         else:
            raise socket.error("Unknown error reading the socket")

    def close(self):
        if self.is_connected():
            if self.use_send_q:            
                self._stopsending()
            self._sock.shutdown(socket.SHUT_WR)

            if self.use_recv_q:
                self._stop_receiving()
            self._sock.shutdown(socket.SHUT_RD)

            self._sock.close()
            self._is_connected = False

    # source: https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
    @classmethod
    def _recvall(self, sock, n):
       # Helper function to recv n bytes or return None if EOF is hit
       data = bytearray()
       while len(data) < n:
          packet = sock.recv(n - len(data))
          if not packet:
              return bytes(b'') # return an empty byte buffer
          data.extend(packet)
       return bytes(data)


if __name__ == "__main__":
   
    ep = EndPoint('127.0.0.1',8080)
    NUM_TEST_CLIENTS = 100
    
    t0 = time.time()
    connector = TCpConnector()
    retries = 10
    for j in range(NUM_TEST_CLIENTS):
         name = "test client " + str(j + 1)
         num_messages = 100
         # - make a single attempt to connect
         connector.connect(ep) # persist(ep,10,1)
         # make retries attempst to connect
         # connector.connectpersist(ep,retries,1,1)
         if connector.is_connected:
            for i in range(num_messages):
               send_msg = Message("[ Message #: " + str(i + 1) + " ]", MessageType.DEFAULT);
               print(f'{name}: Sending:-> {send_msg}')
               # post the message
               connector.postmessage(send_msg)
            
               # read the reply message
               reply_msg = connector.get_message()
               print(f"Echo Reply from server at: {ep} -> {send_msg}")    
            connector.close()
    t1 = time.time()
    print(f"Eplased time: {t1-t0}")