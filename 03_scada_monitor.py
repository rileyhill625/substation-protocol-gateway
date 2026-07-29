"""
03_scada_monitor.py
===================
The SCADA MONITOR: connect to the relay and poll it every second, forever,
applying PROTECTION LOGIC to every reading (alarm on overcurrent or trip).

This is the "supervisor who calls every minute AND has rules." It is the
control-room side of the system and the most job-relevant part of the project.

In the real world, THIS is closest to what you configure: a SCADA master
(like Ignition) polling a relay and raising alarms on thresholds.
"""

import asyncio
from pymodbus.client import AsyncModbusTcpClient

# --- Protection setting ------------------------------------------------------
# PICKUP_A is the current above which we alarm. This is the SAME 0.55 kA pickup
# derived from the pandapower fault study (Project 0), scaled to bench amps.
# Above max load, below min fault -> the protection "window."
PICKUP_A = 55.0

async def monitor():
    client = AsyncModbusTcpClient("127.0.0.1", port=5020)
    await client.connect()
    print("SCADA monitor connected. Polling relay every 1s...\n")

    last_breaker = None             # remembers previous breaker state (for events)

    while True:                     # poll forever (a real monitor never stops)
        # Read current+voltage (2 registers) and breaker (1 coil) each cycle.
        rr = await client.read_holding_registers(address=0, count=2)
        rc = await client.read_coils(address=0, count=1)

        current = rr.registers[0] / 10.0
        voltage = rr.registers[1]
        breaker_closed = rc.bits[0]

        # --- SCADA LOGIC: classify the reading -------------------------------
        if not breaker_closed:
            # Breaker open = the relay tripped = a fault was cleared. Highest alarm.
            status = "*** ALARM: BREAKER OPEN (relay tripped) ***"
        elif current > PICKUP_A:
            # Current over pickup but breaker still closed = overcurrent warning.
            status = f"!! WARNING: overcurrent {current} A > pickup {PICKUP_A} A"
        else:
            status = f"OK  current={current} A  voltage={voltage} V"

        # --- EVENT LOGGING: only announce CHANGES, not every poll ------------
        # Real SCADA logs "events" (state changes), not every identical reading.
        if last_breaker is not None and breaker_closed != last_breaker:
            print(f"  >> EVENT: breaker changed to "
                  f"{'CLOSED' if breaker_closed else 'OPEN'}")
        last_breaker = breaker_closed

        print(status)
        await asyncio.sleep(1)      # wait 1 second, then poll again

if __name__ == "__main__":
    asyncio.run(monitor())