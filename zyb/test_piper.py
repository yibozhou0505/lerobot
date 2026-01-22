from lerobot.robots.piper_follower.piper_follower import PIPERFollower
from lerobot.robots.piper_follower.config_piper_follower import PIPERFollowerConfig
import time

from lerobot.robots.piper_follower.piper_follower import PIPERFollower
from lerobot.robots.piper_follower.config_piper_follower import PIPERFollowerRobotConfig  # 或 PiperFollowerConfig

cfg = PIPERFollowerRobotConfig(
    id="my_piper_follower",   
    can_name="can0",
    # cameras 还没有
)

robot = PIPERFollower(cfg)
robot.connect()

"""

joint_1 (float): 关节1角度 -92000 ~ 92000 / 57324.840764
joint_2 (float): 关节2角度 -2400 ~ 120000 / 57324.840764
joint_3 (float): 关节3角度 3000 ~ -110000 / 57324.840764
joint_4 (float): 关节4角度 -90000 ~ 90000 / 57324.840764
joint_5 (float): 关节5角度 80000 ~ -80000 / 57324.840764
joint_6 (float): 关节6角度 -90000 ~ 90000 / 57324.840764

gripper_pos_range = 0 ~ 0.07 (单位m) 
"""



action = {
    "joint_1.pos": 0,
    "joint_2.pos": 0,
    "joint_3.pos": 0,
    "joint_4.pos": 0,
    "joint_5.pos": 0,
    "joint_6.pos": 0,
    "gripper.pos": 0.06,
}
try:
    for _ in range(500):
        obs = robot.get_observation()
        print({k: round(v, 3) for k,v in obs.items() if k.endswith(".pos")})
        robot.send_action(action)
        time.sleep(0.01)
finally:
    robot.disconnect()
