import asyncio, csv
from datetime import datetime
from asyncua import Client #type:ignore
from opcua import DigitalOutput, AnalogueOutput, DigitalInput, AnalogueInput, get_nodeid

POLL_INTERVAL = 2.0 
READ_TIMEOUT  = 1.0  
CSV_PATH = "normal.csv"

async def main():
	# All analgoue oupits but the time
	analogue_outputs = [anou for anou in AnalogueOutput if anou is not AnalogueOutput.INT_SimulationTime]
	# All the rest
	analogue_inputs = list(AnalogueInput)
	digital_inputs = list(DigitalInput)
	digital_outputs = list(DigitalOutput)
	#Final node list Id's and labels
	all_node = analogue_outputs+analogue_inputs+digital_inputs+digital_outputs
	node_ids = [get_nodeid(an) for an in all_node]
	labels = [an.name for an in all_node]
	async with Client("opc.tcp://10.2.1.10:53530/") as client:
		await client.load_data_type_definitions()
		# Get node
		nodes = [client.get_node(nid) for nid in node_ids]
		# Write to csv
		with open(CSV_PATH, "w", newline= "") as f:
			w = csv.writer(f)
			header = ["timestamp"] + labels
			w.writerow(header)
			print(",".join(header))
			while True:
				# Get with timeout to not get stuck
				tasks = [asyncio.wait_for(n.get_value(), timeout= READ_TIMEOUT) for n in nodes]
				# return exeption to not kill loop
				results = await asyncio.gather(*tasks, return_exceptions= True)
				timestamp= datetime.now().strftime("%H:%M:%S")
				row = [timestamp] + [("" if isinstance(r, Exception) else r) for r in results]
				w.writerow(row)
				f.flush()
				print(",".join(str(x) for x in row))
				# Wait interval then loop 
				await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
