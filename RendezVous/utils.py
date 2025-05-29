from hashlib import sha256
import ipaddress,os

def AnonymizeIP(ip) -> str:
	try:
		salt = os.environ.get('SALT','MYbCMhfZAGyUU0lWkHIIGM3goe3Gty54rVo-1PpTs-w=')
		ipaddress.ip_address(ip)
		hashed = sha256((ip + salt).encode()).hexdigest()
		return hashed
	except ValueError as e:
		raise ValueError(f"Invalid IP: {ip}") from e