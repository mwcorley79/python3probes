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

class Message:
     # Note: the goal for the Message class is to support string (str) and bytes (byte array) types.
     # To do this, we will need to encode string data (using utf-8) to store in byte arrays (binary form).
     # This is not an issue if we make the client of Message handle the encoding ewxplicitly, but instead
     # the goal is for the Messaghe class to handle the encoding implicityly as a convenience to the client.
     # This __init__ provides one way to support this, but we comment this out, and instead provide the 
     # feature using multiple dispatching (for efficiency), which is the Python way of enabling function
     # overloading: see @dispatch below

     def __init__(self, msg_bytes, msg_type=MessageType.DEFAULT):
         self.myinit(msg_bytes, msg_type)

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
     def myinit(self, msg_bytes, msg_type=MessageType.DEFAULT):
        self._msg_data = msg_bytes 
        self._msg_type = msg_type
        # msg set, so pack it (network byte order)
        self._packMsg()

     @dispatch(str, MessageType)
     def myinit(self, msg_bytes, msg_type=MessageType.DEFAULT):
        self._msg_data = msg_bytes.encode("utf-8") 
        self._msg_type = msg_type
        # msg set, so pack it (network byte order)
        self._packMsg()
       
     @dispatch(bytes)
     def setContent(self, new_msg) -> None:
         self._msg_data = new_msg
         # msg set, so pack it (network byte order)
         self._packMsg()

     @dispatch(str)
     def setContent(self, new_msg) -> None:
         self._msg_data = new_msg.encode("utf-8")
         # msg set, so pack it (network byte order)
         self._packMsg()

     # defines a class method, not an instance method
     # https://pynative.com/python-class-method/
     @classmethod
     def Message(cls, msg_type=MessageType.DEFAULT):
         return Message(b'', msg_type)

     def Size(self):
        return len(self._msg_data)

     # https://realpython.com/python-property/
     # using the python property construct (manage attribute) for msg_type instead of a method accessor 
     @property
     def msg_type(self) -> MessageType:
        return self._msg_type

     @msg_type.setter
     def msg_type(self, value):
        self._msg_type = value
        self._packMsg()
   
      # override __str__ special function: use for printing etc
     def __str__(self):
       return self._msg_data.decode("utf-8")

     @property
     def GetContentAsBytes(self) -> bytes:
        return self._msg_data

     @property
     def GetContentAsStr(self) -> str:
        return self._msg_data.decode("utf-8")

     # private function, must be called every there is mofifcation to the 
     # to message. In this way, the up to date message state is packed in network
     # byte order for serialization into network sockets etc.
     # https://docs.python.org/3/library/struct.html
     def _packMsg(self):
       self._packed_msg_hdr = struct.pack('!BI'+str(len(self._msg_data)) + 's', self._msg_type.value, len(self._msg_data), self._msg_data)
     
     def DisplayObjectData(self):
         print(f"Packed (byte) data  : {self._packed_msg_hdr}");
         vals = struct.unpack('!BI'+str(len(self._msg_data)) + 's', self._packed_msg_hdr)
         print(f"Unpacked (byte) data: {vals}");
        
         # print out the unpacked hex and vald
         # https://www.asciitable.com/
         print(f'packed/unpacked (byte) data (in hex): {binascii.hexlify(self._packed_msg_hdr)} -> {vals}\n');


def test_main():
    print("*** Testing Message class operations *** ")
    
    print("Constructing a binary message object (bmsg1)...")
    bmsg1 = Message(b'abc')
    print(f"\"bmsg1\" identity : {id(bmsg1)}")
    print(f"\"bmsg1\" data     : {bmsg1}")
    print(f"\"bmsg1\" len      : {bmsg1.Size()}")
    print(f"\"bmsg1\" type     : {bmsg1.msg_type}")
    
    msg_content = bmsg1.GetContentAsBytes  # uses a property accessor
    print(f"\"bmsg1\" testing (byte) content accessor property:-> {msg_content} -> {type(msg_content)}")
    
    msg_content = bmsg1.GetContentAsStr  # uses a property accessor
    print(f"\"bmsg1\" testing (string) content accessor property:-> {msg_content} -> {type(msg_content)}")
    
    print(f"Display \"bmsg1\" binary (network byte order) packed data")
    bmsg1.DisplayObjectData()
    
    print("Constructing a String (str) message object (strmsg1), encoded as utf-8")
    strmsg1 = Message("string message 1", MessageType.STRING)
    print(f"\"strmsg1\" identity : {id(strmsg1)}")
    print(f"\"strmsg1\" data     : {strmsg1}")
    print(f"\"strmsg1\" len      : {strmsg1.Size()}")
    print(f"\"strmsg1\" type     : {strmsg1.msg_type}")
    print(f"Display \"strmsg1\" binary (network byte order) packed data")
    strmsg1.DisplayObjectData()

    print('\ntesting \"setContent()\" method and \"msg_type\" property \"strmsg1\"')
    strmsg1.setContent("abcde")
    strmsg1.msg_type = MessageType.TEXT
    print(f"\"strmsg1\" identity : {id(strmsg1)}")
    print(f"\"strmsg1\" data     : {strmsg1}")
    print(f"\"strmsg1\" len      : {strmsg1.Size()}")
    print(f"\"strmsg1\" type     : {strmsg1.msg_type}")
    print(f"Display \"strmsg1\" binary (network byte order) packed data")
    strmsg1.DisplayObjectData()

    # using explict syntax, and testing = operator
    strmsg2: Message = strmsg1
    print("testing assignment operator (strmsg2 = strmsg1): ** Notice: id (identity doesn't change, indicating a reference, not a copy **")
    print(f"\"strmsg2\" identity : {id(strmsg1)}")
    print(f"\"strmsg2\" data     : {strmsg1}")
    print(f"\"strmsg2\" len      : {strmsg1.Size()}")
    print(f"\"strmsg2\" type     : {strmsg1.msg_type}")
    print(f"Display \"strmsg2\" binary (network byte order) packed data")
    strmsg2.DisplayObjectData()

   
    print("testing empty message")
    emptyMsg1 = Message.Message()
    print(f"\"emptyMsg1\" identity : {id(emptyMsg1)}")
    print(f"\"emptyMsg1\" data     : {emptyMsg1}")
    print(f"\"emptyMsg1\" len      : {emptyMsg1.Size()}")
    print(f"\"emptyMsg1\" type     : {emptyMsg1.msg_type}")
    print(f"Display \"emptyMsg1\" binary (network byte order) packed data")
    emptyMsg1.DisplayObjectData()

    print("testing empty message # 2")
    emptyMsg2 = Message.Message(MessageType.DISCONNECT)
    print("testing empty2 message")
    print(f"\"emptyMsg2\" identity : {id(emptyMsg2)}")
    print(f"\"emptyMsg2\" data     : {emptyMsg2}")
    print(f"\"emptyMsg2\" len      : {emptyMsg2.Size()}")
    print(f"\"emptyMsg2\" type     : {emptyMsg2.msg_type}")
    print(f"Display \"emptyMsg2\" binary (network byte order) packed data")
    emptyMsg2.DisplayObjectData()


if __name__ == "__main__":
   test_main()

    