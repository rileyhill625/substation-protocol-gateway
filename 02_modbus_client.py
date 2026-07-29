import asyncio
from pymodbus.client import AsyncModbusTcpClient

async def read_relay():
    # Connect to the relay server we started in the other window.
    client = AsyncModbusTcpClient("127.0.0.1", port=5020)
    await client.connect()
    print("Connected to relay at 127.0.0.1:5020\n")

    # Read 2 holding registers starting at address 0 (current, voltage).
    rr = await client.read_holding_registers(address=0, count=2)
    # Read 1 coil at address 0 (breaker status).
    rc = await client.read_coils(address=0, count=1)

    # Pull the values out and un-scale the current (we stored it x10).
    current = rr.registers[0] / 10.0
    voltage = rr.registers[1]
    breaker = "CLOSED" if rc.bits[0] else "OPEN"

    print("=== Relay Readings (via Modbus TCP) ===")
    print(f"  Current : {current} A")
    print(f"  Voltage : {voltage} V")
    print(f"  Breaker : {breaker}")

    client.close()

if __name__ == "__main__":
    asyncio.run(read_relay())