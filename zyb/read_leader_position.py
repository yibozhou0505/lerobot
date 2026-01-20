#!/usr/bin/env python3
import json
import time
from pathlib import Path

from lerobot.motors import Motor, MotorCalibration, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus


def load_calibration_as_objects(path: Path) -> dict[str, MotorCalibration]:
    data = json.loads(path.read_text())

    calib: dict[str, MotorCalibration] = {}
    for name, v in data.items():
        calib[name] = MotorCalibration(
            id=int(v["id"]),
            drive_mode=int(v.get("drive_mode", 0)),
            homing_offset=int(v["homing_offset"]),
            range_min=int(v["range_min"]),
            range_max=int(v["range_max"]),
        )
    return calib

def move_cursor_up(lines):
    """Move the cursor up by a specified number of lines."""
    print(f"\033[{lines}A", end="")

def main():
    port = "/dev/ttyACM0"
    hz = 20
    calib_path = Path("/home/zyb/Code/lerobot/zyb/leader.json")

    calibration = load_calibration_as_objects(calib_path)

    '''degree or 0~100 normalization mode for body motors'''
    # norm_body = MotorNormMode.DEGREES
    norm_body = MotorNormMode.RANGE_M100_100

    bus = FeetechMotorsBus(
        port=port,
        motors={
            "base": Motor(1, "sts3215", norm_body),
            "shoulder": Motor(2, "sts3215", norm_body),
            "elbow": Motor(3, "sts3215", norm_body),
            "wrist_roll1": Motor(4, "sts3215", norm_body),
            "wrist_pitch": Motor(5, "sts3215", norm_body),
            "wrist_roll2": Motor(6, "sts3215", norm_body),
            "gripper": Motor(7, "sts3215", MotorNormMode.RANGE_0_100),
        },
        calibration=calibration,
    )

    bus.connect()
    print(f"Connected to {port}. Ctrl+C to stop.\n")

    names = list(bus.motors.keys())
    dt = 1.0 / hz

    try:
        while True:
            # 归一化后的值（DEGREES or -100..100）
            pos = bus.sync_read("Present_Position")  # dict[name] -> float

            for n in names:
                print(f"{n:12s}  pos={float(pos[n]):9.3f}")

            print("-" * 52)
            time.sleep(dt)
            move_cursor_up(len(names) + 1)

    except KeyboardInterrupt:
        pass
    finally:
        bus.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()
