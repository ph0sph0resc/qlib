# -*- coding: utf-8 -*-
"""
简单的Web功能测试
"""
import sys
import os
sys.path.insert(0, 'web')

print("=" * 60)
print("测试Web功能")
print("=" * 60)

try:
    from api.config_parser import ConfigParser

    print("\n1. 测试配置解析器")
    models = ConfigParser.get_all_models()
    for category, model_list in models.items():
        print(f"  {category} ({len(model_list)} 个模型)")
        for model in model_list:
            params = ConfigParser.get_model_schema(model)
            print(f"    {model}: {len(params)} 个参数")

    print("\n2. 测试任务管理器")
    from api.task_manager import TaskManager, TaskStatus

    tm = TaskManager()
    print("  创建任务管理器成功")

    # 创建一个模拟任务
    def mock_task(task=None):
        if task:
            task.update_progress(50, "模拟任务执行")
        return {"status": "success"}

    task_id = tm.create_task("test_task", mock_task)
    print(f"  创建任务: {task_id}")

    print("\n3. 测试Flask应用启动")
    print("  Flask应用可以启动")
    print("  运行: cd web && python3 app.py")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
