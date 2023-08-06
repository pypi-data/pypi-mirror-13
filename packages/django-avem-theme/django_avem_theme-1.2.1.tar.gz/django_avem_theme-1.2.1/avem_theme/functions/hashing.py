
from base64 import b64encode
import hashlib
from struct import pack


def md5_file(fileobj):
	"""
		Calculate the md5 hash of a file
		Split file into blocks so the entire file doesn't have to be in memory
		Takes about 4.6 sec / GB and about 8kb of memory for any file size
		Make sure the file is open in rb mode
	"""
	md5 = hashlib.md5()
	with fileobj as f:
		for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
			md5.update(chunk)
	return md5.hexdigest()


def float_b64(floatobj, precision = 'f', altchars = '-_'):
	"""
		Base64 encode a float with given precision (f/d).

		Mostly meant for caching flag, not decoding; it uses alt chars and strips the final =
	"""
	bytes = pack(precision, floatobj)
	b64 = b64encode(bytes, altchars = altchars.encode('ascii'))
	return b64.decode('ascii').rstrip('=')


