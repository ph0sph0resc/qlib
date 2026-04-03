#!/usr/bin/env python3
"""测试Qlib文档中的第一个示例"""

import sys
print(f"Python版本: {sys.version}")

# 尝试导入qlib
try:
    import qlib
    print(f"Qlib版本: {qlib.__version__}")
    print(f"Qlib路径: {qlib.__file__}")
except Exception as e:
    print(f"导入qlib失败: {e}")
    sys.exit(1)

# 检查qlib.init
print("\n检查qlib.init...")
import inspect
if hasattr(qlib, 'init'):
    sig = inspect.signature(qlib.init)
    print(f"qlib.init签名: {sig}")
else:
    print("qlib没有init方法")

# 检查qlib.data模块
print("\n检查qlib.data模块...")
try:
    from qlib.data import D
    print("导入qlib.data.D成功")

    # 检查D的方法
    methods = [m for m in dir(D) if not m.startswith('_')]
    print(f"D可用方法: {methods}")
except Exception as e:
    print(f"导入qlib.data.D失败: {e}")

# 检查模型
print("\n检查模型...")
try:
    from qlib.contrib.model.gbdt import GBDTModel
    print("导入GBDTModel成功")
except Exception as e:
    print(f"导入GBDTModel失败: {e}")

# 尝试初始化Qlib
print("\n尝试初始化Qlib...")
try:
    qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")
    print("初始化成功")
except Exception as e:
    print(f"初始化失败: {e}")
    import traceback
    traceback.print_exc()

# 检查数据是否存在
print("\n检查数据...")
try:
    from qlib.data import D
    instruments = D.instruments("csi300")
    print(f"可选资产数量: {len(instruments)}")
except Exception as e:
    print(f"获取资产失败: {e}")
    import traceback
    traceback.print_exc()
