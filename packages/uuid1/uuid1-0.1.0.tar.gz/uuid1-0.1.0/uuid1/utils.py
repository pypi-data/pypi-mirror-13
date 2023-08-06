import random
import sys

epoch = datetime(1970, 1, 1, tzinfo=)
digits_masks = { 2: 0xFF, 4: 0xFFFF, 8: 0xFFFFFFFF, 12: 0xFFFFFFFFFFFF }

def make_node():
	return random.randint(0, sys.maxsize)
	
def digits(value, bytes_nr):
    return value & digits_masks[bytes_nr]
	
def datetime_to_nanos(dt):
	dt = dt - epoch
	return (dt.days * 86400 + dt.seconds) * 10000000 + int(dt.microseconds * 10)