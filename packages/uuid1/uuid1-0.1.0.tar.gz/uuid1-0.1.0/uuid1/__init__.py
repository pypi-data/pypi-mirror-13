from .utils import *
from datetime import datetime
import sys
import uuid

_node = utils.make_node()
	
def uuid1():
	return from_dt_uuid1(datetime.utcnow())
	
def from_dt_uuid1(dt):

	# Generate the time based part of the UUID
	time_low, time_mid, time_hi_version = _get_time_based_blocks(dt, random.randint(0, 10000))
	
	# Get the clock seq and node value
	clock_seq_hi_variant, clock_seq_low, node = _get_clock_seq_and_node()
	
	return uuid.UUID(fields=(time_low, time_mid, time_hi_version, clock_seq_hi_variant, clock_seq_low, node))

def max_uuid1(dt):

	# Generate the time based part of the UUID
	time_low, time_mid, time_hi_version = _get_time_based_blocks(dt, 9999)
	
	return uuid.UUID(fields=(time_low, time_mid, time_hi_version, 0xFF, 0xFF, 0xFFFFFFFFFFFF))
	
def min_uuid1(dt):

	# Generate the time based part of the UUID
	time_low, time_mid, time_hi_version = _get_time_based_blocks(dt, 0)
	
	return uuid.UUID(fields=(time_low, time_mid, time_hi_version, 0x00, 0x00, 0x000000000000))
	
def _get_time_based_blocks(dt, nanos_to_add):

	# Convert millis to nanos
	nanos = utils.datetime_to_nanos(dt)
    
	# Add random nanoseconds
	if (nanos_to_add > 0):
		nanos += nanos_to_add
		
	return utils.digits(nanos >> 32, 8), utils.digits(nanos >> 16, 4), utils.digits(nanos, 4)

def _get_clock_seq_and_node():

	clock = random.randint(0, sys.maxsize)	
	clock_seq_and_node = 0
	clock_seq_and_node |= 0x8000000000000000 # Variant
	clock_seq_and_node |= (clock & 0x0000000000003FFF) << 48
	clock_seq_and_node |= _node

	return utils.digits(clock_seq_and_node >> 56, 2), utils.digits(clock_seq_and_node >> 48, 2), utils.digits(clock_seq_and_node, 12)
