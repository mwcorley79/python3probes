from ClientHandler import * 
from abc import ABC, abstractmethod
from Message import Message, MessageType
from EndPoint import EndPoint 
import threading
import socket

class DefaultClientHandler(ClientHandler):
    #  implement asbtract clone()
    def clone(self):
        '''this is a creational function: you must implement it
           the TCPResponder creates an instance of this class (it's how the server polymorphism works)
        '''
        return DefaultClientHandler()

    #implement application specific processing here
    def app_proc(self):
        msg = self.get_message()
        while msg.msg_type != MessageType.DISCONNECT:
             print(f"From Client: {self.service_ep} -> {msg}");
             
             print(f"Sending echo reply: {msg}");
             self.postmessage(msg);

             msg = self.get_message()
       
class TCPResponder:
      def __init__(self, ep) -> None:
         # super().__init__() excplicity call vbas class ctor
         self._listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self._listen_ep = ep
         self._listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         self._listenSocket.bind( (self._listen_ep.ip, self._listen_ep.port) ) 
         self.isListening = False
         self.numClients = -1
         self.use_recv_q = True
         self.use_send_q = True
         self._ch = DefaultClientHandler()

      def use_client_queues(self, val):
         self.use_recv_q = val
         self.use_send_q = val

      def register_client_handler(self, ch):
         self._ch = ch

      def _listenProc(self, backlog):
        client_count = 0
        self._listenSocket.listen(backlog)
        serviceQ_ = []

        print(f'Listening on: {self._listen_ep}')
        while self.isListening and (client_count < self.numClients): # or self.numClients == -1):
            
            client_sock, addr = self._listenSocket.accept()
            
            client_count += 1
            print(f'Serving Client: {client_count}');
          

            # create an instance of the user supplied client handler
            ch =  self._ch.clone()

            ch.client_socket = client_sock
            ch.service_ep = self._listen_ep

            # service thread to the queue of client connections
            service_client_thread = threading.Thread(target=ch.service_client)
            serviceQ_.append(service_client_thread)
            service_client_thread.start()

        # wait for all service tasks to complete 
        for st in serviceQ_:
            st.join()

      def start(self, backlog=20):
         self.isListening = True
         self._listenThread = threading.Thread(target=self._listenProc, args=(backlog,))
         self._listenThread.start()

      def stop(self):
        if self.isListening:
            try:
             
              self._listenThread.join()
              self._listenSocket.close()
              self.isListening = False
            except:
              self.isListening = False

def test_main():
    NUM_CLIENTS = 100
    addr = EndPoint('127.0.0.1', 8080)
    
    dh = DefaultClientHandler()

    # define instance of the TCPResponder (server host)
    responder = TCPResponder(addr)

    # set number of clients for the server process to service before exiting (-1 runs indefinitely)
    responder.numClients = NUM_CLIENTS

    responder.use_client_queues(True)  # comment if you use SendMessage/ReceiveMessage queues

    responder.register_client_handler(dh)

    #start the server listening thread
    responder.start()
    
    responder.stop()


if __name__ == "__main__":
   test_main()
