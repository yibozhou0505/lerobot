# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
from dataclasses import dataclass
from pathlib import Path

import draccus


@dataclass(kw_only=True)    # 只能用关键字参数,不能用位置参数
class TeleoperatorConfig(draccus.ChoiceRegistry, abc.ABC):
    '''draccus.ChoiceRegistry注册表/选择器基类,允许使用字符串注册子类
    ABC = Abstract Base Class(抽象基类),不一定直接实例化而是给子类继承用
    '''
    # Allows to distinguish between different teleoperators of the same type
    id: str | None = None   # 同一个实例用id区分
    
    # Directory to store calibration file
    calibration_dir: Path | None = None

    @property
    def type(self) -> str:
        return self.get_choice_name(self.__class__)
