"""
This is independent app,you can install it by 
$ pip install tongue
or 
$ easy_install tongue
It's have both class, one is decode and another is code
According the JTT808 protocol,you can use it to make server
know what the terminal say and know say what to terminal!
"""
import struct
import binascii


class Decode:
	"""
	you should initial it by a tuple,just like
	(126,0,1,2,3,4,5,6,7,8,9,126)	
	and then it's should give you a binary code.
	I can show it to here,because you should know why..right?
	It's just call after receive from socket!!
	"""
	def __init__(self,src):
		self.src=src
		self.src_len=len(src)
		self.ruler=struct.Struct('%iB' % (self.src_len))
		self.dst=self.ruler.unpack(self.src)

	
	def show(self):
		print 'src	code:',self.src
		print 'dst	code:',self.dst

class Code:
	"""
	Should give a tuple witch you want to send to the terminal
	it's should be a tuple..
	You should call this before you send it to the terminal !
	"""
	def __init__(self,src):
		self.src=src
		self.src_len=len(src)
		self.ruler=struct.Struct('%iB' % (self.src_len))
		self.temp=self.ruler.pack(*self.src)
		self.bar=binascii.hexlify(self.temp)
		self.dst=binascii.unhexlify(self.bar)
		

	
	def show(self):
		print 'src	code:',self.src
		print 'dst	code:',self.dst

if __name__ == '__main__':
	"""
	We need some binary guys,so let binascii.unhexlify help us
	example below:ascii '7e800100029911'
	"""
	packed_data=binascii.unhexlify('7e8001000299117e')
	example = Decode(packed_data)
	example.show()
	
	
	tuple_data=(126,1,2,0,153,45,76)
	example2=Code(tuple_data)
	example2.show()
