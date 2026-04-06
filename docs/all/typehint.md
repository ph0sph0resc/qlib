# typehint.py 模块文档

## 文件概述
提供Qlib常用的类型提示，支持Python 3.8+的typing特性。

## 类型定义

### InstDictConf 类
**功能：** 基于字典的实例配置类型（TypedDict）

**配置格式示例：**

**情况1：指定类名**
```python
{
    "class": "ClassName",
    "kwargs": {},  # 可选，默认为{}
    "module_path": "path.to.module",  # 可选
}
```

**情况2：直接指定类**
```python
{
    "class": <TheClass>,
    "kwargs": {},
}
```

**字段说明：**
- `class`: 类对象或类名（Python中class是关键字，所以用注释）
- `kwargs`: 字典，默认为空字典
- `module_path`: 模块路径字符串，可选

**用途：** 描述如何实例化一个对象

---

### InstConf 类型别名
**类型：** `Union[InstDictConf, str, object, Path]`

**功能：** 实例配置的联合类型

**支持的格式：**

1. **InstDictConf**（字典配置）
   - 参见上面的InstDictConf示例

2. **str**（字符串）
   - 情况1：pickle对象路径
     - 格式：`"file:///<path to pickle file>/obj.pkl"`
   - 情况2：类名
     - 格式：`"ClassName"`，使用默认模块
   - 情况3：模块路径+类名
     - 格式：`"a.b.c.ClassName"`

3. **object**（对象实例）
   - 如果是accept_types的实例，直接返回

4. **Path**（路径对象）
   - 指定pickle对象路径
   - 等同`"file:///<path>"`格式

**示例：**
```python
from qlib.typehint import InstConf

# 字典配置
config1: InstConf = {
    "class": "LGBModel",
    "module_path": "qlib.contrib.model.gbdt",
    "kwargs": {"loss": "mse"}
}

# 字符串类名
config2: InstConf = "LGBModel"  # 使用默认模块

# 模块路径+类名
config3: InstConf = "qlib.contrib.model.gbdt.LGBModel"

# pickle文件路径
config4: InstConf = "file:///path/to/model.pkl"

# 直接对象
config5: InstConf = some_model_instance

# Path对象
from pathlib import Path
config6: InstConf = Path("/path/to/model.pkl")
```

## 使用示例

### 类型注解
```python
from typing import Dict
from qlib.typehint import InstConf

def init_model(config: InstConf) -> object:
    """初始化模型"""
    from qlib.utils import init_instance_by_config
    return init_instance_by_config(config)
```

### 配置定义
```python
from qlib.typehint import InstDictConf

# 定义模型配置
model_config: InstDictConf = {
    "class": "LGBModel",
    "module_path": "qlib.contrib.model.gbdt",
    "kwargs": {
        "loss": "mse",
        "learning_rate": 0.05,
    }
}
```

### 函数签名
```python
from typing import Optional
from qlib.typehint import InstConf

def load_instance(
    config: Optional[InstConf] = None
) -> Optional[object]:
    if config is None:
        return None
    from qlib.utils import init_instance_by_config
    return init_instance_by_config(config)
```

## 版本兼容性

### Python 3.8+
```python
from qlib.typehint import Literal, TypedDict, final

# 使用Literal
freq: Literal["1min", "5min", "1h", "1d"] = "1min"

# 使用TypedDict
config: TypedDict = {
    "name": str,
    "value": int,
}

# 使用final
@final
class MyClass:
    pass
```

### Python 3.7及以下
```python
# 自动从typing_extensions导入
from qlib.typehint import Literal, TypedDict, final
```

## 类型注解场景

### 配置文件注解
```python
from typing import Dict
from qlib.typehint import InstConf

# 工作流配置类型
WorkflowConfig = Dict[
    str,  # 键：如"model", "dataset"
    InstConf  # 值：可以是各种配置格式
]
```

### 函数参数注解
```python
from typing import List, Optional
from qlib.typehint import InstConf

def create_instances(
    configs: List[InstConf],
    default_module: Optional[str] = None
) -> List[object]:
    """从配置列表创建实例"""
    from qlib.utils import init_instance_by_config
    instances = []
    for config in configs:
        instance = init_instance_by_config(
            config,
            default_module=default_module
        )
        instances.append(instance)
    return instances
```

## 与其他模块的关系
- `typing`: Python标准类型模块
- `typing_extensions`: Python 3.7类型支持
- `pathlib`: 路径处理（InstConf支持Path）
- `qlib.utils.mod`: 使用这些类型提示

## 最佳实践

1. **使用InstConf进行类型检查**
   - 提供灵活的配置接口
   - 支持多种配置格式

2. **使用TypedDict定义配置结构**
   - 提高类型安全性
   - 支持IDE自动完成

3. **使用Literal限制选项**
   - 明确指定允许的值
   - 防止无效配置

4. **版本兼容性**
   - 代码同时支持Python 3.7和3.8+
   - 自动选择合适的导入
