import platform
import socket
import os
import time
import subprocess
import struct
#import ansa

'''
Implementation of the Inter ANSA Protocol (IAP). IAP is a protocol that is to
be used for the communication between ANSA processes. The first traffic cases
supported aimed at the execution of python scripts on remote ANSA processes.

A remote ANSA process is started in listener mode waiting for incoming
connections. Once a HelloRequest is sent the handshake is started and when
HelloResponse is successful the remote ANSA process is ready to execute
incoming python scripts. To terminate the connection a GoodbyeRequest is sent.
'''

## Enumerations ##
class MessageCode:
	'''
	Provide information on what specific message is being exchanged, which
in turn defines what kind of operation should be invoked by the receiving peer.
'''
	hello = 0x01
	execute_script = 0x02
	goodbye = 0x03

class MessageType:
	'''
	Type of message being exchanged.
	'''
	response = 0x00
	request = 0x01

class Tag:
	'''
	Tag of the Information Element TLV. What kind / purpose of information
is carried by the element.
	'''
	result_code = 0x01
	process_id = 0x02
	script_string = 0x03
	entry_method = 0x04
	script_return_type = 0x05
	script_retval_string_dict = 0x06
	script_execution_details = 0x07
	supported_service = 0x08
	post_connection_action = 0x09
	pre_execution_database_action = 0x0a
	script_retval_bytes = 0x0b
	color_indicator = 0x0c
	event_code = 0x0d
	muted_execution = 0x0e

class Services:
	'''
	Services defined.
	'''
	common = 0x00
	script_execution = 0x01

class ResultCode:
	'''
	Values for the Tag.result_code.
	'''
	success = 0x00
	internal_error = 0x01
	operation_error = 0x02
	no_compatible_sevices = 0x03

class ScriptReturnType:
	'''
	Values for the Tag.script_return_type.
	'''
	none = 0x00
	unsupported = 0x01
	string_dict = 0x02
	type_bytes = 0x03

class ScriptExecutionDetails:
	'''
	Values for the Tag.script_execution_details.
	'''
	success = 0x00
	temp_file_failed = 0x01
	exception_raised = 0x02
	script_not_loaded = 0x03
	unknown_error = 0x04

class PostConnectionAction:
	'''
	Values for the Tag.post_connection_action.
	'''
	shut_down = 0x00
	keep_listening = 0x01

class PreExecutionDatabaseAction:
	'''
	Values for the Tag.pre_execution_database_action.
	'''
	reset_database = 0x00
	keep_database = 0x01

class MutedExecution:
	'''
	Values for the Tag.muted_execution.
	'''
	off = 0x00
	on = 0x01
## ~Enumerations ##



## Auxiliary functions
def calculate_padding_octets(length):
	length_mod_4 = length % 4
	if length_mod_4 == 0:
		return 0

	return 4 - length_mod_4

def pack_padding_octets(btext):
	padding_octets = calculate_padding_octets(len(btext))
	if padding_octets == 0:
		return b''

	octets = b'\xa5' * padding_octets

	return struct.pack('>%ds' % (len(octets),) , octets)

def pack_btext(btext):
	p = struct.pack('>%ds' % (len(btext),) , btext)

	return p + pack_padding_octets(btext)

def decode_tlvs(octets, ies_length):
	ies = []
	ie_start = 0

	while ies_length > 0:
		length = struct.unpack('>L', octets[ie_start + 4 : ie_start + 8])[0]

		ie = InformationElement.frombytes(octets[ie_start : ie_start + length])
		ies.append(ie)

		value_length = length - 4 - 4

		padding_octets = calculate_padding_octets(value_length)

		total_length = length + padding_octets

		ie_start += total_length

		ies_length -= total_length

	return ies

def decode_tag(tag):
	if tag == Tag.result_code:
		return 'Tag.result_code'
	elif tag == Tag.process_id:
		return 'Tag.process_id'
	elif tag == Tag.script_string:
		return 'Tag.script_string'
	elif tag == Tag.entry_method:
		return 'Tag.entry_method'
	elif tag == Tag.script_return_type:
		return 'Tag.script_return_type'
	elif tag == Tag.script_retval_string_dict:
		return 'Tag.script_retval_string_dict'
	elif tag == Tag.script_retval_bytes:
		return 'Tag.script_retval_bytes'
	elif tag == Tag.script_execution_details:
		return 'Tag.script_execution_details'
	elif tag == Tag.supported_service:
		return 'Tag.supported_service'
	elif tag == Tag.post_connection_action:
		return 'Tag.post_connection_action'
	elif tag == Tag.pre_execution_database_action:
		return 'Tag.pre_execution_database_action'
	elif tag == Tag.color_indicator:
		return 'Tag.color_indicator'
	elif tag == Tag.muted_execution:
		return 'Tag.muted_execution'
	else:
		return 'Unknown Tag'

def pack_ies(ies):
	packed_ies = list(map(lambda ie: ie.pack(), ies))
	return b''.join(packed_ies)
## ~Auxiliary functions




class MessageHeader():
	'''Messages consist of a Header, plus an arbitrary number of Information Elements coded as TLVs (Tag - Length - Value).
	version: Version of the protocol. Only 0x01 defined at the moment
	flags: Flags providing additional information on the message. Only MessageType values defined at the moment
	service_id: Information on the Service that this message supports (e.g. Remote Script Execution)
	message_code: Information on what specific message is being exchanged
	transaction_id: An integer used to identify and correlate a Request / Response pair. Increased by 1 after each transaction
	length: The length of the complete message in octets, i.e. covers the header + all TLVs
	'''
	def __init__(self, version, message_type, service_id, message_code, transaction_id, length):
		self.version = version                   # B : unsigned char
		self.flags = message_type                # B : unsigned char
		self.service_id = service_id             # H : unsigned short
		self.message_code = message_code	 # L : unsigned long
		self.transaction_id = transaction_id     # L : unsigned long
		self.length = length                     # L : unsigned long

	def payload_len(self):
		return 16

	def pack(self):
		return struct.pack('>BBHLLL', self.version, self.flags, self.service_id, self.message_code, self.transaction_id, self.length)

	@classmethod
	def frombytes(cls, octets):
		data = struct.unpack('>BBHLLL', octets)
		return cls(*data)




class InformationElement():
	'''
	The information elements are used to carry the specifics for an operation. They are encoded using a straightforward Tag - Length - Value format.
	tag: What kind / purpose of information is carried by the element. The tag also defines how the value is encoded / decoded.
	length: The length of the complete TLV in octets, i.e. covers all 3 sections
	value: Holds the actual data that are to be transferred

	Padding octets are added after the end of the value part, so that the total length of the encoded information element is a multiple of 4 octets. Note: the length field does not included the padding octets!
	'''
	def __init__(self, tag, value):
		self.tag = tag                          # L : unsigned long
		self.value = value

	def __repr__(self):
		return 'InofrmationElement(%r, %r)' % (self.tag, self.value)

	def __str__(self):
		return '%s, %r' % (decode_tag(self.tag), self.value)

	def pack(self):
		if isinstance(self.value, int):
			return struct.pack('>LLI', self.tag, 12, self.value)
		elif isinstance(self.value, str):
			btext = self.value.encode('utf-8')

			p = struct.pack('>LL', self.tag, 4 + 4 + len(btext))

			return p + pack_btext(btext)
		elif isinstance(self.value, bytes):
			p = struct.pack('>LL', self.tag, 4 + 4 + len(self.value))

			return p + pack_btext(self.value)
		else:
			raise TypeError('Unkown value type: ' + type(self.value))

	@classmethod
	def frombytes(cls, octets):
		tag = struct.unpack('>L', octets[:4])[0]

		if tag in [Tag.result_code, Tag.process_id, Tag.script_return_type, \
				Tag.script_execution_details, Tag.supported_service, Tag.post_connection_action, Tag.muted_execution]:
			value = struct.unpack('>L', octets[-4:])[0]
			return cls(tag, value)
		elif tag in [Tag.script_string, Tag.entry_method]:
			value = octets[8 : 8 + length].decode('utf-8')
			return cls(tag, value)
		elif tag in [Tag.script_retval_string_dict]:
			return cls(tag, octets)
		elif tag in [Tag.script_retval_bytes]:
			value = bytes(octets[8:])
			return cls(tag, value)
		else:
			return None


class Response:
	def __init__(self, octets):
		header = MessageHeader.frombytes(octets[:16])

		self.ies = decode_tlvs(octets[16:], header.length - 16)

	def success(self):
		if self.get_result_code() == ResultCode.success:
			return True

		return False

	def get_result_code(self):
		'''
		Returns the ResultCode
		'''
		for ie in self.ies:
			if ie.tag == Tag.result_code:
				return ie.value

		return None


class HelloRequest():
	'''
	Initialize connection
	'''
	def __init__(self, process_id, transaction_id):
		self.header = MessageHeader(1, MessageType.request, Services.common, MessageCode.hello, transaction_id, 0)
		self.process_id = process_id              # L : unisnged long

	def message(self):
		ies = []
		ies.append(InformationElement(Tag.process_id, self.process_id))
		ies.append(InformationElement(Tag.supported_service, 0x00010002))

		packed_ies = pack_ies(ies)
		self.header.length = self.header.payload_len() + len(packed_ies)

		return self.header.pack() + packed_ies


class HelloResponse(Response):
	def __init__(self, octets):
		super().__init__(octets)


class RunScriptTextRequest():
	'''
	Execute a script text

	e.g. "def main():\n print('main is called')"
	'''
	def __init__(self, script_text, function_name, pre_execution_database_action, transaction_id):
		self.header = MessageHeader(1, MessageType.request, Services.script_execution, MessageCode.execute_script, transaction_id, 0)
		self.text = script_text
		self.function_name = function_name
		self.pre_execution_database_action = pre_execution_database_action
		self.muted_execution = MutedExecution.off

	def message(self):
		ies = []
		ies.append(InformationElement(Tag.script_string, self.text))

		if self.function_name:
			ies.append(InformationElement(Tag.entry_method, self.function_name))

		ies.append(InformationElement(Tag.pre_execution_database_action, self.pre_execution_database_action))

		if self.muted_execution != MutedExecution.off:
			ies.append(InformationElement(Tag.muted_execution, self.muted_execution))

		packed_ies = pack_ies(ies)
		self.header.length = self.header.payload_len() + len(packed_ies)

		return self.header.pack() + packed_ies


class RunScriptFileRequest():
	'''
	Execute a script file

	Script execution results are sent back through the RunScriptFileResponse message. It can be either None, or a dictionary with strings as keys and data.
	'''
	def __init__(self, filepath, function_name, pre_execution_database_action, transaction_id):
		self.header = MessageHeader(1, MessageType.request, Services.script_execution, MessageCode.execute_script, transaction_id, 0)
		self.filepath = filepath
		self.function_name = function_name
		self.pre_execution_database_action = pre_execution_database_action
		self.muted_execution = MutedExecution.off
		self.text = ''

	def message(self):
		with open(self.filepath, 'r') as fp:
			self.text = fp.read()

		ies = []
		ies.append(InformationElement(Tag.entry_method, self.function_name))
		ies.append(InformationElement(Tag.script_string, self.text))
		ies.append(InformationElement(Tag.pre_execution_database_action, self.pre_execution_database_action))

		if self.muted_execution != MutedExecution.off:
			ies.append(InformationElement(Tag.muted_execution, self.muted_execution))
			
		packed_ies = pack_ies(ies)
		self.header.length = self.header.payload_len() + len(packed_ies)

		return self.header.pack() + packed_ies


class RunScriptResponse(Response):
	def __init__(self, octets):
		super().__init__(octets)

	def get_script_execution_details(self):
		'''
		Returns a ScriptExecutionDetails
		'''
		for ie in self.ies:
			if ie.tag == Tag.script_execution_details:
				return ie.value

		return None

	def get_script_return_type(self):
		'''
		Returns a ScriptReturnType
		'''
		for ie in self.ies:
			if ie.tag == Tag.script_return_type:
				return ie.value

		return None

	def _bytes_to_string_dict(self, octets):
		ret_dict = {}

		dict_len_index = 8
		dict_len = struct.unpack('>L', octets[dict_len_index : dict_len_index + 4])[0]

		index_e = dict_len_index + 4
		for i in range(dict_len):
			index_s = index_e
			index_e = index_s + 4
			key_len = struct.unpack('>L', octets[index_s : index_e])[0]

			index_s = index_e
			index_e = index_s + key_len
			key_val = octets[index_s : index_e]

			index_s = index_e
			index_e = index_s + 4
			data_len = struct.unpack('>L', octets[index_s : index_e])[0]

			index_s = index_e
			index_e = index_s + data_len
			data_val = octets[index_s : index_e]

			ret_dict[key_val.decode('utf-8')] = data_val.decode('utf-8')

		return ret_dict

	def get_response_dict(self):
		'''
		Get the dictionary returned by the remote script.
		'''
		for ie in self.ies:
			if ie.tag == Tag.script_retval_string_dict:
				return self._bytes_to_string_dict(ie.value)

		return None

	def get_response_bytes(self):
		'''
		Get the bytes returned by the remote script
		'''
		for ie in self.ies:
			if ie.tag == Tag.script_retval_bytes:
				return ie.value

		return None


class GoodbyeRequest():
	'''
	Terminate connection and inform the remote peer what to do after through the post_connection_action option.
	'''
	def __init__(self, post_connection_action, transaction_id):
		self.header = MessageHeader(1, MessageType.request, Services.common, MessageCode.goodbye, transaction_id, 0)
		self.post_connection_action = post_connection_action

	def message(self):
		ie_connection_action = InformationElement(Tag.post_connection_action, self.post_connection_action)

		packed_ies = ie_connection_action.pack()
		self.header.length = self.header.payload_len() + len(packed_ies)

		return self.header.pack() + packed_ies


class GoodbyeResponse(Response):
	def __init__(self, octets):
		super().__init__(octets)


class AnsaProcess():
	'''
	Main class for running an ANSA process in Listener mode and execute python scripts on it
	'''
	def __init__(self, ansa_command = None, run_in_batch = True, other_running_options = None):
		if not ansa_command:
			ansa_command = self._get_ansa_command()

		self.host = 'localhost'
		self.port = self._free_port()
		self.server = '@'.join((str(self.port), self.host))

		cmd = [ansa_command, '-nolauncher', '-listenport', str(self.port), '-foregr']
		if run_in_batch:
			cmd.append('-b')

		if other_running_options:
			cmd.extend(list(other_running_options))

		self.ansa_process = subprocess.Popen(cmd, shell = False)

	def get_iap_connection(self):
		return IAPConnection(self.port)

	def _get_ansa_command(self):
		path = ansa.constants.app_root_dir

		penv = platform.uname()

		if penv[0] == 'Darwin' or penv[0] == 'Linux':
			ansa_command = os.path.join(path, 'ansa.sh')
		elif penv[0] == 'Windows':
			ansa_command = os.path.join(path, 'ansa.bat')
		else:
			raise EnvironmentError('ERROR Unknown Operating System.')

		return ansa_command

	def _free_port(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('', 0))
		port = s.getsockname()[1]
		s.close()
		return port

class IAPConnection():
	'''
	Class that handles messaging to ANSA running in Listener mode
	'''
	def __init__(self, port):
		self.ansa_control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.transaction_id = 0

		retry = True
		count_tries = 0
		while retry:
			try:
				self.ansa_control.connect(('localhost', port))
			except socket.error:
				retry = True
			else:
				self._inform_user('Connected to ANSA')
				retry = False

			count_tries += 1
			if count_tries > 10: self._inform_user('Trying to connect ...')
			if count_tries > 60:
				raise EnvironmentError('ERROR Cannot start ANSA')

			time.sleep(1)

	def _inform_user(self, text):
		print('IAP Connection: '+text)

	def _get_transaction_id(self):
		ret = self.transaction_id
		self.transaction_id += 1
		return ret

	def recv(self):
		resp = self.ansa_control.recv(16)

		length = struct.unpack('>L', resp[-4:])[0]

		return resp + self.ansa_control.recv(length)

	def hello(self):
		'''Handshake with the remote ANSA process

		A HelloRequest is sent and a HelloResponse is received.
		'''
		request = HelloRequest(os.getpid(), self._get_transaction_id())

		self.ansa_control.sendall(request.message())

		resp = self.recv()

		return HelloResponse(resp)

	def run_script_file(self, filepath, function_name, pre_execution_database_action = PreExecutionDatabaseAction.reset_database, muted_execution=MutedExecution.off):
		''' Execute a function from a python script file

		The function can return a dictionary with strings as key and data. This dictionary will be returned trough RunScriptResponse.
		'''
		request = RunScriptFileRequest(filepath, function_name, pre_execution_database_action, self._get_transaction_id())
		request.muted_execution = muted_execution

		self.ansa_control.sendall(request.message())

		resp = self.recv()

		return RunScriptResponse(resp)

	def run_script_text(self, script_text, function_name = None, pre_execution_database_action = PreExecutionDatabaseAction.reset_database, muted_execution=MutedExecution.off):
		''' Execute a string script
		'''
		request = RunScriptTextRequest(script_text, function_name, pre_execution_database_action, self._get_transaction_id())
		request.muted_execution = muted_execution

		self.ansa_control.sendall(request.message())

		resp = self.recv()

		return RunScriptResponse(resp)

	def goodbye(self, post_connection_action):
		''' Terminate connection

		A GoodbyeRequest is sent and a GoodbyeResponse is received.
		'''
		request = GoodbyeRequest(post_connection_action, self._get_transaction_id())

		self.ansa_control.sendall(request.message())

		resp = self.recv()

		return GoodbyeResponse(resp)

	def close(self):
		self.ansa_control.close()
