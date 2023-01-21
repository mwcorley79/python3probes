import pybq as BlockingQueue
import socket
from EndPoint import EndPoint
from Message import *

# import the module support for abstract classes (not avaible by default in Python)
# Abstract classes in python https://www.geeksforgeeks.org/abstract-classes-in-python/
# Liscov subsutition in Python: https://www.pythontutorial.net/python-oop/python-liskov-substitution-principle/
from abc import ABC, abstractmethod

class ClientHandler(ABC):
    def __init__(self) -> None:
        self._sendQ = BlockingQueue.BQueue()
        self._recvQ = BlockingQueue.BQueue()
        self.is_receiving = False
        self.is_sending = False
        self.use_send_queue = True
        self.use_recv_queue = True
       
    @abstractmethod
    def clone(self):
        pass
    
    @abstractmethod
    def app_proc():
        pass

    @property
    def client_socket(self):
        return self._sock

    @client_socket.setter
    def client_socket(self, sock):
         self._sock = sock

    @property
    def service_ep(self) -> EndPoint:
        return self._service_ep

    @service_ep.setter
    def service_ep(self, ep):
        self._service_ep = ep

    def postmessage(self, msg): 
        self._sendQ.enQ(msg)

    def sendsessage(self, msg):
        self._sendsocketmessage(msg)

    def _sendsocketmessage(self, msg):
        self._sock.sendall(msg.get_serialized_message)

    def _send_proc(self):
        try:
            msg = self._sendQ.deQ()
            while msg.msg_type != MessageType.STOP_SENDING:
               self._sendsocketmessage(msg)
               msg = self._sendQ.deQ()
        except Exception as e:
            print(f"Error in _send_proc() {e}")
             
    def _start_sending(self):
        if not self.is_sending:
            self.is_sending = True
            self._send_thread = threading.Thread(target=self._send_proc)
            self._send_thread.start()

    def _stop_sending(self):
        try:
          if self.is_sending:
             self.postmessage(Message.empty_init(MessageType.STOP_SENDING))
             #self.post_message (Message.empty_init(MessageType.STOP_SENDING))
             self._send_thread.join()
             self.is_sending = False
        except:
            self.is_sending = False

    def _shutdown_send(self):
        self._sock.shutdown(socket.SHUT_WR)

    def _shutdown_recv(self):
        self._sock.shutdown(socket.SHUT_RD)
  
    def close(self):
        self._sock.close()

    def _start_receiving(self):
        if not self.is_receiving:
            self.is_receiving = True
            self._recv_thread = threading.Thread(target=self._recv_proc)
            self._recv_thread.start()

    def _recv_proc(self):
        try:
            # receive msh from the socket
            msg =  self._receive_socket_message()

            # if not the DISCONNECT signal, then copy (reference) into the receive blocking queue
            while msg.msg_type != MessageType.DISCONNECT:
               self._recvQ.enQ(msg)
               msg =  self._receive_socket_message()
            self._recvQ.enQ(msg)
        except Exception as e: 
            print(f'Error in _recv_proc(): {e}')

    def _stop_receiving(self):
        try:
          if self.is_receiving:
             self._recv_thread.join()
             self.is_receiving = False
        except:
            self.is_receiving = False

    def recv_message(self):
        return self._receive_socket_message()

    def get_message(self):
        return self._recvQ.deQ()


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

    def UseClientQueues(self, val):
        self.use_send_queue = val
        self.use_recv_queue = val

    def service_client(self):
        try:
          # start the client processing thread, if use specifies to 
          if self.use_recv_queue:
             self._start_receiving()

          if self.use_send_queue:
             self._start_sending()

          self.app_proc()
        except Exception as e:
            print(f"service_client start error: {e}")
 
        try:
          # start the client processing thread, if use specifies to 
          if self.use_recv_queue:
            self._stop_receiving()
          self._shutdown_recv()

          if self.use_send_queue:
            self._stop_sending()
          self._shutdown_send()
          
          self.close()
        except Exception as e:
             print(f"service_client stop error: {e}")


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