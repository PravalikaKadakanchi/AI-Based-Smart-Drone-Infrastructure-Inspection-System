"""
Telemetry interface for the Pixhawk flight controller via MAVLink.

Provides GPS coordinates, altitude, battery, and flight-mode data.
Falls back to simulated telemetry when no Pixhawk is connected, so the
dashboard and report pipeline remain fully testable off-hardware.
"""

import time
import random
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from pymavlink import mavutil  # type: ignore

    PYMAVLINK_AVAILABLE = True
except ImportError:
    PYMAVLINK_AVAILABLE = False


@dataclass
class TelemetrySnapshot:
    latitude: float
    longitude: float
    altitude_m: float
    battery_percent: float
    flight_mode: str
    armed: bool
    timestamp: float


class TelemetryReader:
    """Unified telemetry reader with automatic hardware/simulation fallback."""

    # Default simulated location: reference point for demo flights.
    _SIM_ORIGIN = (17.3850, 78.4867)  # Hyderabad, India

    def __init__(self, connection_string: str, baudrate: int = 57600, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode or not PYMAVLINK_AVAILABLE
        self._master = None

        if not self.simulation_mode:
            self._master = mavutil.mavlink_connection(connection_string, baud=baudrate)
            self._master.wait_heartbeat(timeout=10)
            logger.info("MAVLink heartbeat received from Pixhawk.")
        else:
            logger.info("Telemetry running in SIMULATION mode (no Pixhawk attached).")

    def read(self) -> TelemetrySnapshot:
        if self.simulation_mode:
            return self._simulated_snapshot()
        return self._live_snapshot()

    def _live_snapshot(self) -> TelemetrySnapshot:
        msg = self._master.recv_match(
            type=["GLOBAL_POSITION_INT", "SYS_STATUS", "HEARTBEAT"],
            blocking=True,
            timeout=5,
        )
        gps = self._master.messages.get("GLOBAL_POSITION_INT")
        sys_status = self._master.messages.get("SYS_STATUS")
        heartbeat = self._master.messages.get("HEARTBEAT")

        return TelemetrySnapshot(
            latitude=(gps.lat / 1e7) if gps else 0.0,
            longitude=(gps.lon / 1e7) if gps else 0.0,
            altitude_m=(gps.relative_alt / 1000) if gps else 0.0,
            battery_percent=(sys_status.battery_remaining) if sys_status else -1,
            flight_mode=mavutil.mode_string_v10(heartbeat) if heartbeat else "UNKNOWN",
            armed=bool(heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) if heartbeat else False,
            timestamp=time.time(),
        )

    def _simulated_snapshot(self) -> TelemetrySnapshot:
        lat, lon = self._SIM_ORIGIN
        jitter = 0.0006  # roughly ~60m wander for a realistic demo flight path
        return TelemetrySnapshot(
            latitude=lat + random.uniform(-jitter, jitter),
            longitude=lon + random.uniform(-jitter, jitter),
            altitude_m=round(random.uniform(8, 25), 1),
            battery_percent=round(random.uniform(55, 100), 1),
            flight_mode=random.choice(["GUIDED", "AUTO", "LOITER"]),
            armed=True,
            timestamp=time.time(),
        )

    def close(self):
        if not self.simulation_mode and self._master is not None:
            self._master.close()
