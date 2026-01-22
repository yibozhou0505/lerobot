import time
from dataclasses import dataclass
from typing import Dict

from piper_sdk import C_PiperInterface_V2


@dataclass
class PiperMotorsBusConfig:
    can_name: str
    motors: dict[str, tuple[int, str]]

class PiperMotorsBus:
    """
        对Piper SDK的二次封装
    """
    def __init__(self, 
                 config: PiperMotorsBusConfig):
        self.piper = C_PiperInterface_V2(config.can_name)
        self.piper.ConnectPort()
        self.motors = config.motors
        # 录制数据集时改成0
        self.init_joint_position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # [6 joints + 1 gripper] * 0.0
        self.safe_disable_position = [0.0, 0.0, 0.0, 0.0, 0.52, 0.0, 0.0]
        self.pose_factor = 1000 # 单位 0.001mm
        # self.joint_factor = 1000 # 度 -> 0.001度
        self.joint_factor = 57324.840764 # 1000*180/3.14， rad -> 度（单位0.001度）

    @property
    def motor_names(self) -> list[str]:
        return list(self.motors.keys())

    @property
    def motor_models(self) -> list[str]:
        return [model for _, model in self.motors.values()]

    @property
    def motor_indices(self) -> list[int]:
        return [idx for idx, _ in self.motors.values()]


    def connect(self, enable:bool, timeout:float = 5.0) -> bool:
        """ 
        使能机械臂, 5s内检测使能状态, 返回是否使能成功
        """
        start = time.time()
        if enable:
            self.piper.EnableArm(7)
            self.piper.GripperCtrl(0,1000,0x01, 0)
        else:
            self.piper.DisableArm(7)
            self.piper.GripperCtrl(0,1000,0x02, 0)

        while time.time() - start < timeout:
            msg = self.piper.GetArmLowSpdInfoMsgs()
            enabled_list = [
                msg.motor_1.foc_status.driver_enable_status,
                msg.motor_2.foc_status.driver_enable_status,
                msg.motor_3.foc_status.driver_enable_status,
                msg.motor_4.foc_status.driver_enable_status,
                msg.motor_5.foc_status.driver_enable_status,
                msg.motor_6.foc_status.driver_enable_status,
            ]
            all_enabled = all(enabled_list)

            # 目标：enable=True  -> all_enabled True
            # 目标：enable=False -> all_enabled False
            if all_enabled == enable:
                print(f"[OK] enable={enable}, status={all_enabled}, list={enabled_list}")
                return True
            time.sleep(0.2)

        print(f"[TIMEOUT] enable={enable} not reached within {timeout}s")
        return False


    def set_calibration(self):
        return
    
    def revert_calibration(self):
        return

    def apply_calibration(self):
        """
            移动到初始位置
        """
        self.write(target_joint=self.init_joint_position)

    def apply_calibration_master(self):
        """
            master移动到初始位置
        """
        self.write(target_joint=self.init_joint_position)
        

    def write(self, target_joint:list):
        """
            Joint control
            - target joint: in radians
                joint_1 (float): 关节1角度 -92000 ~ 92000 / 57324.840764
                joint_2 (float): 关节2角度 -2400 ~ 120000 / 57324.840764
                joint_3 (float): 关节3角度 3000 ~ -110000 / 57324.840764
                joint_4 (float): 关节4角度 -90000 ~ 90000 / 57324.840764
                joint_5 (float): 关节5角度 80000 ~ -80000 / 57324.840764
                joint_6 (float): 关节6角度 -90000 ~ 90000 / 57324.840764
                gripper_range: 夹爪角度 0~0.08
        """
        joint_0 = round(target_joint[0]*self.joint_factor)
        joint_1 = round(target_joint[1]*self.joint_factor)
        joint_2 = round(target_joint[2]*self.joint_factor)
        joint_3 = round(target_joint[3]*self.joint_factor)
        joint_4 = round(target_joint[4]*self.joint_factor)
        joint_5 = round(target_joint[5]*self.joint_factor)
        gripper_range = round(target_joint[6]*1000*1000)
        
        self.piper.MotionCtrl_2(0x01, 0x01, 100, 0x00)
        self.piper.JointCtrl(joint_0, joint_1, joint_2, joint_3, joint_4, joint_5)
        self.piper.GripperCtrl(abs(gripper_range), 1000, 0x01, 0) 

    def read(self) -> Dict:
        """
            - 机械臂关节消息,单位0.001度
            - 机械臂夹爪消息,单位0.001mm
        """
        joint_msg = self.piper.GetArmJointMsgs()
        joint_state = joint_msg.joint_state

        gripper_msg = self.piper.GetArmGripperMsgs()
        gripper_state = gripper_msg.gripper_state

        states = {
            "joint_1": joint_state.joint_1,
            "joint_2": joint_state.joint_2,
            "joint_3": joint_state.joint_3,
            "joint_4": joint_state.joint_4,
            "joint_5": joint_state.joint_5,
            "joint_6": joint_state.joint_6,
            "gripper": gripper_state.grippers_angle
        }

        return states


    def safe_disconnect(self):
        """ 
            Move to safe disconnect position
        """
        self.write(target_joint=self.safe_disable_position)

    def safe_disconnect_master(self):
        """ 
            Move to safe disconnect position
        """
        self.write_master(target_joint=self.safe_disable_position)