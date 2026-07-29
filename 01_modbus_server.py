import asyncio
from pymodbus.datastore import ModbusServerContext, ModbusDeviceContext, ModbusSequentialDataBlock
from pymodbus.server import StartAsyncTcpServer

# pymodbus 3.14 API; migrates to SimData/SimDevice in v4. Blocks start at address 1.
breaker_coil    = ModbusSequentialDataBlock(1, [1, 0, 0, 0, 0])        # coil 1 = breaker closed
relay_registers = ModbusSequentialDataBlock(1, [600, 12470, 0, 0, 0])  # reg 1 = current x10, reg 2 = voltage

store = ModbusDeviceContext(co=breaker_coil, hr=relay_registers)
context = ModbusServerContext(devices=store, single=True)

async def run_server():
    print("Relay Modbus server on 127.0.0.1:5020 (reg1=current x10, reg2=voltage, coil1=breaker)")
    await StartAsyncTcpServer(context, address=("127.0.0.1", 5020))

if __name__ == "__main__":
    asyncio.run(run_server())