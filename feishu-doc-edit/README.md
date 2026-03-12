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
