"""
02_modbus_client.py
===================
A simple ONE-SHOT Modbus client: connect to the relay, read its values once,
print them, disconnect. This is the "supervisor makes a single phone call."

This proves the round-trip works. The continuous version is in 03.
"""

import asyncio
from pymodbus.client import AsyncModbusTcpClient
# AsyncModbusTcpClient = the "phone" that dials a Modbus server over TCP.

async def read_relay():
    # Point the client at the same address+port the server is listening on.
    client = AsyncModbusTcpClient("127.0.0.1", port=5020)
    await client.connect()          # open the connection ("dial the number")
    print("Connected to relay at 127.0.0.1:5020\n")

    # --- Read the data --------------------------------------------------------
    # read_holding_registers(address=0, count=2) = "give me 2 registers starting
    # at address 0." NOTE: clients address 0-based, even though the server stored
    # starting at 1 -> this is the classic Modbus off-by-one. reg[0] = current.
    rr = await client.read_holding_registers(address=0, count=2)

    # read_coils(address=0, count=1) = "give me 1 coil at address 0" (breaker).
    rc = await client.read_coils(address=0, count=1)

    # --- Interpret the raw values --------------------------------------------
    current = rr.registers[0] / 10.0        # undo the x10 scaling -> 39.5 A
    voltage = rr.registers[1]               # already in volts -> 12470
    breaker = "CLOSED" if rc.bits[0] else "OPEN"

    print("=== Relay Readings (via Modbus TCP) ===")
    print(f"  Current : {current} A")
    print(f"  Voltage : {voltage} V")
    print(f"  Breaker : {breaker}")

    client.close()                  # hang up

if __name__ == "__main__":
    asyncio.run(read_relay())