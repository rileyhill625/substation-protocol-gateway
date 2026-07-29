import asyncio
from pymodbus.client import AsyncModbusTcpClient

# Protection thresholds (the "settings" a real SCADA/relay would use)
PICKUP_A = 55.0      # alarm above this current (your 0.55 kA pickup, scaled to bench amps)

async def monitor():
    client = AsyncModbusTcpClient("127.0.0.1", port=5020)
    await client.connect()
    print("SCADA monitor connected. Polling relay every 1s...\n")

    last_breaker = None
    while True:
        rr = await client.read_holding_registers(address=0, count=2)
        rc = await client.read_coils(address=0, count=1)

        current = rr.registers[0] / 10.0
        voltage = rr.registers[1]
        breaker_closed = rc.bits[0]

        # SCADA logic: classify and alarm
        if not breaker_closed:
            status = "*** ALARM: BREAKER OPEN (relay tripped) ***"
        elif current > PICKUP_A:
            status = f"!! WARNING: overcurrent {current} A > pickup {PICKUP_A} A"
        else:
            status = f"OK  current={current} A  voltage={voltage} V"

        # Only announce breaker state CHANGES (real SCADA logs events, not every poll)
        if breaker_closed != last_breaker and last_breaker is not None:
            print(f"  >> EVENT: breaker changed to {'CLOSED' if breaker_closed else 'OPEN'}")
        last_breaker = breaker_closed

        print(status)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(monitor())