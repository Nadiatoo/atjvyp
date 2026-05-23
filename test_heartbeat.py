#!/usr/bin/env python3
import datetime

now = datetime.datetime.now()
print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"是否为工作日: {'是' if now.weekday() in [0,1,2,3,4] else '否'}")

# 下一个任务时间
task_time = datetime.datetime.strptime(f"{now.strftime('%Y-%m-%d')} 17:00", "%Y-%m-%d %H:%M")
if task_time <= now:
    tomorrow = now + datetime.timedelta(days=1)
    task_time = datetime.datetime.strptime(f"{tomorrow.strftime('%Y-%m-%d')} 17:00", "%Y-%m-%d %H:%M")

hours_until = (task_time - now).total_seconds() / 3600
print(f"下一个任务: 今天17:00（盘后分析）")
print(f"距离下一个任务: {hours_until:.1f}小时")

if hours_until < 2:
    print("建议: 执行详细心跳检查")
    exit(0)
else:
    print("建议: 简单返回HEARTBEAT_OK，跳过详细检查")
    exit(1)