---
name: feishu-doc-edit
description: "飞书文档编辑操作指南，重点解决图片插入位置不准确的问题。包含正确的 index 定位方法、多图顺序插入策略、替换图片流程、常见故障排查。"
---

# Skill: 飞书文档编辑（含图片精确插入）

## 适用场景
- 在飞书文档中插入/替换图片，并让图片出现在指定位置
- 编辑文档内容（文字、标题、代码块、表格）
- 批量操作文档 block

---

## 核心工具

| 工具 | 用途 |
|------|------|
| `feishu_doc list_blocks` | 获取文档所有 block 及其 children 顺序 |
| `feishu_doc get_block` | 获取单个 block 详情（含 children 数组） |
| `feishu_doc upload_image` | 上传图片并插入到指定位置 |
| `feishu_doc delete_block` | 删除指定 block |
| `feishu_doc insert` | 插入文字/标题等内容 block |
| `feishu_doc update_block` | 修改 block 内容 |

---

## 图片插入：正确姿势

### ⚠️ 关键限制（必读）

1. **飞书 API 不支持移动 block**。图片一旦插入位置错了，只能删掉重新插。
2. `after_block_id` 参数**不可靠**，实测经常把图片追加到文档末尾而不是指定位置后面。
3. **唯一可靠的定位方式**：用 `index` 参数（0-based，在 parent 的 children 数组中的位置）。

### 正确流程

```
第一步：获取文档结构，确定插入位置的 index
  feishu_doc list_blocks → 找到目标 block 在 children 数组中的位置 N
  图片要插在该 block 之后 → index = N + 1

第二步：上传图片，指定 index
  feishu_doc upload_image
    doc_token: <文档token>
    file_path: <本地图片路径>
    parent_block_id: <父block，通常是文档根节点>
    index: N+1   ← 关键！

第三步：验证位置
  feishu_doc get_block (doc_token) → 检查 children 数组，确认图片 block_id 在正确位置
```

### 替换已有图片

```
第一步：list_blocks 找到旧图片的 block_id 和它在 children 中的 index N
第二步：delete_block 删除旧图片
第三步：upload_image 用同样的 index N 插入新图片
        （删除后原位置的 index 不变，后续 block 前移）
```

### 多张图片按顺序插入

每插入一张图片后，后续所有 block 的 index 都会 +1。
**必须从后往前插入**，或者每次插入后重新 list_blocks 确认最新 index。

```
错误做法：
  图1 → index 10
  图2 → index 15   ← 此时图1已经占了 index 10，图2实际应该是 16

正确做法（从后往前）：
  先插图3（最靠后的）→ index 39
  再插图2 → index 24  （图3不影响图2前面的 index）
  再插图1 → index 19  （图2、图3都在后面，不影响）
```

---

## 常见操作示例

### 在某段文字后插入图片

```python
# 1. 获取文档结构
blocks = feishu_doc.list_blocks(doc_token="XXX")

# 2. 找到目标文字 block 在 children 中的位置
children = blocks[0]["children"]  # 根节点的 children
target_id = "doxcnXXX"  # 目标文字 block_id
idx = children.index(target_id)  # 比如 idx = 18

# 3. 上传图片到 idx+1
feishu_doc.upload_image(
    doc_token="XXX",
    file_path="/tmp/screenshot.jpg",
    parent_block_id="XXX",  # 文档根节点 token
    index=idx + 1  # = 19
)
```

### 删除并重新插入图片

```python
# 找到图片 block
img_block_id = "doxcnYYY"
img_index = children.index(img_block_id)  # 比如 22

# 删除
feishu_doc.delete_block(block_id=img_block_id, doc_token="XXX")

# 重新插入（index 不变，因为删除后后面的 block 前移了）
feishu_doc.upload_image(
    doc_token="XXX",
    file_path="/tmp/new_image.jpg",
    parent_block_id="XXX",
    index=img_index  # 仍然是 22
)
```

---

## 图片对齐设置

上传后图片默认居中（align=2）。如需修改：

```python
feishu_doc.update_block(
    block_id="doxcnZZZ",
    doc_token="XXX",
    # align: 1=左对齐, 2=居中, 3=右对齐
    image={"align": 1}
)
```

---

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| 图片出现在文档末尾 | `after_block_id` 不可靠 | 改用 `index` 参数 |
| index 偏移 | 之前插入操作改变了 children 顺序 | 每次操作后重新 `list_blocks` 确认 |
| 多张图片顺序错乱 | 从前往后插入导致 index 累积偏移 | 改为从后往前插入 |
| 图片上传成功但看不到 | 文档权限问题 | 检查 `feishu_perm` |

---

## 注意事项

- `parent_block_id` 通常填文档根节点（即 `doc_token` 本身），除非要插入到某个容器 block（如表格单元格）内
- 飞书文档 block 类型 27 = 图片
- `list_blocks` 返回的 children 数组顺序 = 文档中从上到下的显示顺序
- 删除 block 后，该位置之后的所有 block index 自动 -1
