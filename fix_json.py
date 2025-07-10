import json

path = "page_ranges.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 自动嵌套非数组页码配置
for k in data:
    if isinstance(data[k], list) and len(data[k]) == 2 and isinstance(data[k][0], int):
        data[k] = [data[k]]  # 包一层 []

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已修复 page_ranges.json：所有配置已转换为嵌套数组形式 [[start, end]]")
