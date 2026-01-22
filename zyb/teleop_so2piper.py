#!/usr/bin/env python3
import json
import time
from pathlib import Path

from lerobot.motors import Motor, MotorCalibration, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

from lerobot.robots.piper_follower.piper_follower import PIPERFollower
from lerobot.robots.piper_follower.config_piper_follower import PIPERFollowerConfig
import time

from lerobot.robots.piper_follower.piper_follower import PIPERFollower
from lerobot.robots.piper_follower.config_piper_follower import PIPERFollowerRobotConfig  # 或 PiperFollowerConfig
import math









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
    print("start")
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



    # ================ piper_follower =================
    cfg = PIPERFollowerRobotConfig(
    id="my_piper_follower",   
    can_name="can0",
    # cameras 还没有
    )

    robot = PIPERFollower(cfg)
    robot.connect()

    JOINT_FACTOR = 57324.840764 

    PIPER_LIMITS_CNT = {
        "joint_1": (-92000,  92000),
        "joint_2": ( -2400, 120000),
        "joint_3": (  3000,-110000),  
        "joint_4": (-90000,  90000),
        "joint_5": ( 80000, -80000), 
        "joint_6": (-90000,  90000),
    }

    PIPER_LIMITS_RAD = {}
    for j,(a,b) in PIPER_LIMITS_CNT.items():
        lo = min(a,b) / JOINT_FACTOR
        hi = max(a,b) / JOINT_FACTOR
        PIPER_LIMITS_RAD[j] = (lo, hi)

    # Normalization
    def clamp(x, lo, hi):
        return max(lo, min(hi, x))

    def norm_to_rad(n, lo, hi):
        n = clamp(n, -100.0, 100.0)

        if n >= 0:
            # 0..100 -> 0..hi
            return (n / 100.0) * hi
        else:
            # -100..0 -> lo..0
            return (-n / 100.0) * lo

    LEADER_TO_PIPER = {
        "base": "joint_1",
        "shoulder": "joint_2",
        "elbow": "joint_3",
        "wrist_roll1": "joint_4",
        "wrist_pitch": "joint_5",
        "wrist_roll2": "joint_6",
    }

    GAIN = {
    "base": -1.0,
    "shoulder": -1.0,
    "elbow": -1.0,
    "wrist_roll1": -1.0,
    "wrist_pitch": -1.0,
    "wrist_roll2": -1.0,
    }






    try:
        input("Move leader & piper to desired ZERO pose, then press ENTER to set reference...")
        leader_ref = bus.sync_read("Present_Position")

        while True:
            pos = bus.sync_read("Present_Position")  # dict[name] -> float
            action = {}
            for l_name, p_name in LEADER_TO_PIPER.items():
                n = (pos[l_name] - leader_ref[l_name]) * GAIN[l_name]
                lo, hi = PIPER_LIMITS_RAD[p_name]
                q = norm_to_rad(n, lo, hi)
                action[f"{p_name}.pos"] = q
                print(f"{l_name:12s}  norm={n:9.3f}  ->  {p_name:8s}  rad={q:9.3f}")
            action["gripper.pos"] = clamp(pos["gripper"] / 100.0 * 0.07, 0.0, 0.07)  # gripper 0~0.07m

            robot.send_action(action)


            # for n in names:
            #     print(f"{n:12s}  pos={float(pos[n]):9.3f}")

            # print("-" * 52)
            # # move_cursor_up(len(names) + 1)
            # obs = robot.get_observation()
            # for k, v in obs.items():
            #     if k.endswith(".pos"):
            #         print(f"{k}: {round(v, 3)}")
            # move_cursor_up(15)


            time.sleep(dt)
    except KeyboardInterrupt:
        pass
    finally:
        robot.disconnect()
        bus.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()
