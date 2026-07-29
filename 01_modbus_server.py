"""
01_modbus_server.py
====================
Simulates a PROTECTIVE RELAY that serves live data over Modbus TCP.

Think of this as the "security guard": it holds values (current, voltage,
breaker status) in numbered slots and waits for a client to ask for them.

In a real substation this role is played by an actual SEL/GE/ABB relay.
We build it in Python so we understand what that relay is doing underneath.
"""

import asyncio
# asyncio = Python's tool for doing things "concurrently" (waiting for network
# connections without freezing). A server must wait for clients, so it needs this.

from pymodbus.datastore import (
    ModbusServerContext,        # the whole server's memory (can hold many devices)
    ModbusDeviceContext,        # one device's memory (our single relay)
    ModbusSequentialDataBlock,  # a block of numbered storage slots
)
from pymodbus.server import StartAsyncTcpServer
# StartAsyncTcpServer = the function that actually opens a network port and listens.

# --- Define the relay's data -------------------------------------------------
# Modbus storage comes in types. We use two:
#   COILS  = single on/off bits   (e.g. breaker open/closed)
#   HOLDING REGISTERS = 16-bit whole numbers (e.g. current, voltage)
#
# NOTE: pymodbus 3.14 quirk -> data blocks start at address 1, not 0.
# NOTE: registers hold WHOLE numbers only, so 39.5 A is stored as 395 ("x10 scaling").

breaker_coil = ModbusSequentialDataBlock(1, [1, 0, 0, 0, 0])
#   coil 1 = 1  -> breaker CLOSED (in service). 0 would mean OPEN (tripped).

relay_registers = ModbusSequentialDataBlock(1, [600, 12470, 0, 0, 0])
#   register 1 = 395   -> current = 39.5 A (stored x10)
#   register 2 = 12470 -> voltage = 12470 V

# --- Assemble the device -----------------------------------------------------
# Put the coil block and register block into one "device" (our relay).
#   co = coils, hr = holding registers (di = discrete inputs, ir = input registers)
store = ModbusDeviceContext(co=breaker_coil, hr=relay_registers)

# Wrap the device in a server context. single=True means "just one device here."
context = ModbusServerContext(devices=store, single=True)

# --- Run the server ----------------------------------------------------------
async def run_server():
    # "async def" = this function can run concurrently with other tasks.
    print("Relay Modbus server on 127.0.0.1:5020 "
          "(reg1=current x10, reg2=voltage, coil1=breaker)")
    # 127.0.0.1 = "this same computer" (localhost). Port 5020 avoids needing
    # admin rights (the real Modbus default, 502, requires elevated privileges).
    await StartAsyncTcpServer(context, address=("127.0.0.1", 5020))
    # "await" = start this and wait here. The server now listens forever.

if __name__ == "__main__":
    # This runs only when you launch the file directly (python 01_modbus_server.py).
    # asyncio.run() starts the event loop. IMPORTANT: this only works from a real
    # terminal/script, NOT inside Jupyter (Jupyter already has a running loop).
    asyncio.run(run_server())