# feishu-doc-edit

飞书文档编辑 skill，重点解决**图片精确插入位置**的问题。

## 用途

- 在飞书文档指定位置插入图片
- 替换已有图片
- 批量按顺序插入多张图片
- 编辑文档文字/标题/表格等内容

## 核心结论（避坑）

`after_block_id` 参数不可靠，图片会跑到文档末尾。**必须用 `index` 参数定位。**

## 使用方法

### 1. 在指定位置插入图片

```python
# 先获取文档结构，找到目标 block 的位置
feishu_doc list_blocks doc_token=<token>

# 找到目标 block 在 children 数组中的 index N
# 上传图片到 N+1 位置
feishu_doc upload_image
  doc_token=<token>
  file_path=<本地图片路径>
  parent_block_id=<文档根节点token>
  index=<N+1>
```

### 2. 替换图片

```
1. list_blocks → 找到旧图片的 block_id 和 index N
2. delete_block 删除旧图片
3. upload_image 用同样的 index N 插入新图片
```

### 3. 多张图片按顺序插入

**从后往前插入**，避免 index 累积偏移：

```
先插最靠后的图片 → 再插中间的 → 最后插最前面的
```

## 关键参数

| 参数 | 说明 |
|------|------|
| `doc_token` | 文档 token，从 URL `/docx/XXX` 提取 |
| `parent_block_id` | 通常填文档根节点（同 doc_token） |
| `index` | 0-based，在 parent children 数组中的插入位置 |
| `block_id` | 单个 block 的 ID，从 list_blocks 获取 |

## 注意事项

- 每次插入/删除操作后，后续 block 的 index 会变化，需重新 `list_blocks` 确认
- 图片 block 类型为 27
- 默认居中对齐（align=2），可通过 `update_block` 修改

## 详细指南

见同目录 `SKILL.md`。

---

## 注册与调用（AI 自动发现）

### 安装后如何让 AI 自动调用

本 skill 已注册到 MemOS public memory，AI agent 可通过 `skill_search` 检索到。

**触发关键词：** 飞书文档、图片插入、文档编辑、feishu doc、upload image

**AI 调用方式：**
```
skill_search("飞书文档图片插入")
→ 找到 feishu-doc-edit
→ 读取 ~/.openclaw/skills/feishu-doc-edit/SKILL.md
→ 按照 SKILL.md 中的步骤操作
```

### 手动注册（如果 skill_search 找不到）

```bash
# 1. 发布并写入注册队列
python3 ~/.openclaw/workspace/local-skill-creator/scripts/publish_skill.py \
  ~/.openclaw/skills/feishu-doc-edit --owner "马振坤"

# 2. AI agent 执行注册
python3 ~/.openclaw/workspace/local-skill-creator/scripts/register_memos.py
# → 读取队列，调用 memory_write_public
# → 注册完成后清空队列
python3 ~/.openclaw/workspace/local-skill-creator/scripts/register_memos.py --clear
```

### GitHub

https://github.com/mkz0930/openclaw-watchdog-skill-library/tree/master/feishu-doc-edit
