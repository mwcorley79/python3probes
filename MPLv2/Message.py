# Message class is develped to support creating variable-sized binary, and string (utf-8 encoded)
# messages with a specified (prefined) message type.  The primary purpose of the this class is
# support use with an eventual socket-based communication system.
# 
# The communication system will extend a previous Rust and C++ comparison experiment 
# (primarily performance based) by Dr. James Fawcett and Mike Corley 
# Here: https://jimfawcett.github.io/CommCompare.html.
# The Message is part of the dvelopment need to extend that experient to include Python   

# The Message class also a provide a means to experiment with Python 
# constructs:  
#  struct - for packing byte data for C language compatability
#      https://docs.python.org/3/library/struct.html
# properties:
#    https://realpython.com/python-property/
# multiple dispatching (for function overloading)
#    https://www.geeksforgeeks.org/python-method-overloading/

# others:
# references used for byte packing
# https://pymotw.com/2/socket/binary.html
# https://www.golinuxcloud.com/python-struct-module/
# https://docs.python.org/3/library/struct.html

# references used for enums:
# https://docs.python.org/3/howto/enum.html

# ascii table ref:
# https://www.asciitable.com/

# binary encodings ref:
# https://www.geeksforgeeks.org/working-with-binary-data-in-python/

# multiple dispatch decorator (support for function overloading)
# https://www.geeksforgeeks.org/python-method-overloading/

# class methods, versus indtance methods
# https://pynative.com/python-class-method/


# Run command: python .\Message.py

from enum import IntEnum
import threading
import binascii
import sys
import struct
import sys

from multipledispatch import dispatch
  # pip3 install multipledispatch

# all of the message types supported by class Message
class MessageType(IntEnum):
    DEFAULT = 0,
    TEXT = 1,
    REPLY = 2,
    END = 4,
    QUIT = 8,
    DISCONNECT = 16,
    STOP_SENDING = 32,
    STRING = 64,
    BINARY = 128

    # override special __str__ method using _name_ attribute to get str representation for display
    # (name) representation for printing
    def __str__(self):
        return self._name_

# this class serves at the wire format for Message class for C#, for Python compatibility,
# used for transmission over network sockets.
# ref:  https://docs.python.org/3/library/struct
class PackedMessage:   
   # Interpret bytes as packed binary data, suitable to serialize into a TCP socket.
   # note: big endian (network) byte order. Compatibel with C++, C#, and Rust (over the network) 
   def __init__(self, msg_bytes, msg_type=MessageType.DEFAULT):
       self._packed_msg = struct.pack('!BI'+str(len(msg_bytes)) + 's', msg_type, len(msg_bytes), msg_bytes)
   
   @classmethod
   def hdr_len(self): 
      return 5;  # fix this later

   @property
   def get_serialized_message(self):
      return self._packed_msg

   @classmethod
   def extract_message_attribs(self, raw_hdr):
      # hdr will always be BE, so check endianness of the platform to determine how to interpret
      # if sys.byteorder == 'little':
      #   hdr_attribs = struct.unpack('<BI', raw_hdr)
      #else:
      # unpack the first 5 bytes of the header
      hdr_attribs = struct.unpack('!BI', raw_hdr[0:5])
      return hdr_attribs 

class Message:
     # Note: the goal for the Message class is to support string (str) and bytes (byte array) types.
     # To do this, we will need to encode string data (using utf-8) to store in byte arrays (binary form).
     # This is not an issue if we make the client of Message handle the encoding ewxplicitly, but instead
     # the goal is for the Messaghe class to handle the encoding implicityly as a convenience to the client.
     # This commented out __init__ provides one way to support this, but instead we provide the 
     # myinit using multiple dispatching (for efficiency), which is the Python way of enabling function
     # overloading: see @dispatch below. 

     def __init__(self, msg_bytes, msg_type=MessageType.DEFAULT):
         self.init(msg_bytes, msg_type)

         # msg now set, so pack it (network byte order)
         #self._packed_msg_hdr = self._packMsg()
         
         # if its a string encode it (utf-8), 
         #if isinstance(msg_bytes, str):
         #   self._msg_data = msg_bytes.encode("utf-8"))
         # else:
         #   self._msg_data = msg_bytes

         # self._msg_type = msg_type
         # msg set, so pack it (network byte order)
         # self._packMsg()

     # @dispatch - multiple dispatch decorator (support for function overloading)
     # https://www.geeksforgeeks.org/python-method-overloading/
     @dispatch(bytes, MessageType)
     def init(self, msg_bytes, msg_type=MessageType.DEFAULT):
        self._msg_data = msg_bytes 
        self._msg_type = msg_type
       
     @dispatch(str, MessageType)
     def init(self, msg_str, msg_type=MessageType.DEFAULT):
        self._msg_data = msg_str.encode("utf-8") 
        self._msg_type = msg_type

     # defines a class method (not an instance method) used
     # instantiate message with empty mesg_data (contents)
     # https://pynative.com/python-class-method/
     @classmethod
     def empty_init(cls, msg_type=MessageType.DEFAULT):
         return Message(b'', msg_type)
   
     @classmethod
     def from_string(cls, str_msg) -> bytes:
        return str_msg.encode("utf-8")

     # https://realpython.com/python-property/
     # using the python property construct (manage attribute) for msg_data (content) instead of a method accessor 
     @property
     def content(self) -> bytes:
        return self._msg_data

     @content.setter
     def content(self, msg_data):
        self._msg_data = msg_data
    
     # https://realpython.com/python-property/
     # using the python property construct (manage attribute) for msg_type instead of a method accessor 
     @property
     def msg_type(self) -> MessageType:
        return self._msg_type

     @msg_type.setter
     def msg_type(self, value):
        self._msg_type = value
     
     @property
     def content_len(self):
        return len(self._msg_data)

      # override __str__ special function: use for printing etc
     def __str__(self):
       return self._msg_data.decode("utf-8")

     def to_string(self) -> str:
        return self.__str__()

     @property
     def get_serialized_message(self): 
        return  PackedMessage(self.content, self.msg_type).get_serialized_message
     
     @classmethod
     def display_message_data(cls, msg):
         # print(f"Packed (byte) data  : {msg.get_serialized_message}");
         
         # save as example:  unpacks the header -> (1-byte tyoe 4-byte content length), and the message 
         # vals = struct.unpack('!BI'+str(len(self._msg_data)) + 's', self._packed_msg_hdr)
         # print(f"Unpacked (byte) data: {vals}");
        
         # print out the unpacked hex and vald
         # https://www.asciitable.com/
         print(f'Packed (binary) message (in hex): {binascii.hexlify(msg.get_serialized_message)}\n');
         # print(f'packed/unpacked (byte) data (in hex): {binascii.hexlify(self._packed_msg_hdr)} -> {vals}\n');

def test_main():
    print("*** Testing Message class operations *** ")
    
    print("Constructing a binary message object (bmsg1)...")
    bmsg1 = Message(b'abc')
    print(f"\"bmsg1\" identity : {id(bmsg1)}")
    print(f"\"bmsg1\" data     : {bmsg1}")
    print(f"\"bmsg1\" len      : {bmsg1.content_len}")
    print(f"\"bmsg1\" type     : {bmsg1.msg_type}")
    
    msg_content = bmsg1.content # uses a property accessor
    print(f"\"bmsg1\" testing (byte) content accessor property:-> {msg_content} -> {type(msg_content)}")
    
    msg_content = bmsg1.to_string()  # uses a property accessor
    print(f"\"bmsg1\" testing (string) content accessor property:-> {msg_content} -> {type(msg_content)}")
    
    print(f"Display \"bmsg1\" binary (network byte order) packed data")
    Message.display_message_data(bmsg1)


    print("Constructing a String (str) message object (strmsg1), encoded as utf-8")
    strmsg1 = Message("string message 1", MessageType.STRING)
    print(f"\"strmsg1\" identity : {id(strmsg1)}")
    print(f"\"strmsg1\" data     : {strmsg1}")
    print(f"\"strmsg1\" len      : {strmsg1.content_len}")
    print(f"\"strmsg1\" type     : {strmsg1.msg_type}")
    print(f"Display \"strmsg1\" binary (network byte order) packed data")
    Message.display_message_data(strmsg1);

    print('\nTesting \"content\" and \"msg_type\" property \"strmsg1\"')
    strmsg1.content = Message.from_string("abcde")
    strmsg1.msg_type = MessageType.TEXT
    print(f"\"strmsg1\" identity : {id(strmsg1)}")
    print(f"\"strmsg1\" data     : {strmsg1}")
    print(f"\"strmsg1\" len      : {strmsg1.content_len}")
    print(f"\"strmsg1\" type     : {strmsg1.msg_type}")
    print(f"Display \"strmsg1\" binary (network byte order) packed data")
    Message.display_message_data(strmsg1)

    # using explict syntax, and testing = operator
    strmsg2: Message = strmsg1
    print("testing assignment operator (strmsg2 = strmsg1): ** Notice: id (identity doesn't change, indicating a reference, not a copy **")
    print(f"\"strmsg2\" identity : {id(strmsg2)}")
    print(f"\"strmsg2\" data     : {strmsg2}")
    print(f"\"strmsg2\" len      : {strmsg2.content_len}")
    print(f"\"strmsg2\" type     : {strmsg1.msg_type}")
    print(f"Display \"strmsg2\" binary (network byte order) packed data")
    Message.display_message_data(strmsg2)

   
    print("testing empty message")
    emptyMsg1 = Message.empty_init()
    print(f"\"emptyMsg1\" identity : {id(emptyMsg1)}")
    print(f"\"emptyMsg1\" data     : {emptyMsg1}")
    print(f"\"emptyMsg1\" len      : {emptyMsg1.content_len}")
    print(f"\"emptyMsg1\" type     : {emptyMsg1.msg_type}")
    print(f"Display \"emptyMsg1\" binary (network byte order) packed data")
    Message.display_message_data(emptyMsg1)

    print("testing empty message # 2")
    emptyMsg2 = Message.empty_init(MessageType.DISCONNECT)
    print("testing empty2 message")
    print(f"\"emptyMsg2\" identity : {id(emptyMsg2)}")
    print(f"\"emptyMsg2\" data     : {emptyMsg2}")
    print(f"\"emptyMsg2\" len      : {emptyMsg2.content_len}")
    print(f"\"emptyMsg2\" type     : {emptyMsg2.msg_type}")
    print(f"Display \"emptyMsg2\" binary (network byte order) packed data")
    Message.display_message_data(emptyMsg2)

    # test property accessor 
    print("testing \"get_serialized_message\" property accessor")
    msg = Message("this is message for testing the property/accessor", MessageType.STRING)
    
    # test serialized binary (packed) message for transmission over socket
    print(f'The message is: {msg}')
    data = msg.get_serialized_message
    print(f'\"msg\"  -> serialized message data is: {binascii.hexlify(data)}')
    print(f'\"msg\" len is: { len(data)  }')
    print(f"Content len : {msg.content_len}");

    print("test message header extraction method: \"ExtractMessageAttribs\"")
    vals = PackedMessage.extract_message_attribs(data)
    print(f"Message type: {MessageType(vals[0])}");
    print(f"Content len : {vals[1]}");
  
if __name__ == "__main__":
   test_main()

    