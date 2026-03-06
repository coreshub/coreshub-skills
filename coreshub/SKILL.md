---
name: coreshub
description: 查询和管理基石智算（CoreshHub）平台资源，包括 EPFS 文件系统、容器实例（Notebook）、分布式训练任务、推理服务和 iMaaS 大模型服务。通过命令行脚本与 CoreshHub API 交互，输出 JSON 格式结果。
---

# CoreshHub 平台资源查询 Skill

## 前提条件：环境变量配置

在调用任何脚本之前，确保以下环境变量已设置：

```bash
export QY_ACCESS_KEY_ID="<基石智算 Access Key>"
export QY_SECRET_ACCESS_KEY="<基石智算 Secret Key>"
export CORESHUB_USER_ID="<基石智算账户 ID>"

# 可选：自定义可用区域（不设置则使用默认值 xb3,xb2,hb2）
export CORESHUB_ZONES="xb3:西北3区,xb2:西北2区,hb2:华北2区"
```

> 如果用户没有提供这些信息，请先询问用户获取，不要猜测。

## 脚本位置

所有脚本位于 `coreshub/scripts/` 目录下。调用前先切换到该目录，或使用相对路径：

```bash
# 示例（从项目根目录）
python coreshub/scripts/epfs.py --help
```

## 可用脚本一览

| 脚本 | 功能 | 主要命令 |
|------|------|---------|
| `epfs.py` | EPFS 弹性并行文件系统 | `list`, `bill`, `zones` |
| `container.py` | 容器实例（Notebook） | `list`, `ssh`, `zones` |
| `training.py` | 分布式训练任务 | `list`, `logs`, `zones` |
| `inference.py` | 推理服务 | `list`, `logs`, `zones` |
| `imaas.py` | iMaaS 大模型服务 | `models`, `model`, `apikeys`, `metrics`, `zones` |

---

## 详细命令说明

### 1. EPFS 文件系统（epfs.py）

#### 列出文件系统

```bash
python coreshub/scripts/epfs.py list \
  --zone xb3 \
  --owner <user_id> \
  --user-id <user_id> \
  [--limit 10] [--offset 0]
```

- `--zone`：区域标识，可选 xb3（西北3区）/ xb2（西北2区）/ hb2（华北2区）
- `--owner` / `--user-id`：账户 ID，可从 `CORESHUB_USER_ID` 环境变量自动读取

#### 查询账单信息

```bash
python coreshub/scripts/epfs.py bill \
  --zone xb3 \
  --owner <user_id> \
  --user-id <user_id> \
  --resource-id <resource_id>
```

- `--resource-id`：资源 ID，**必填**，从 `list` 命令返回的 `resource_id` 字段获取

---

### 2. 容器实例（container.py）

#### 列出容器实例

```bash
python coreshub/scripts/container.py list \
  --zone xb3 \
  [--limit 10] [--offset 0] [--name "关键字"]
```

返回字段包含：`uuid`、`namespace`、`name`、`status` 等

#### 获取 SSH / 端口访问信息

```bash
python coreshub/scripts/container.py ssh \
  --zone xb3 \
  --uuid <uuid> \
  [--namespace <namespace>] \
  [--owner <user_id>] \
  [--user-id <user_id>] \
  [--services "ssh,custom,node_port"]
```

- `--uuid`：**必填**，从 `list` 命令返回的 `uuid` 字段获取
- `--namespace`：命名空间，默认为账户 ID 小写
- `--services`：要开启的服务，默认 `ssh,custom,node_port`

---

### 3. 分布式训练（training.py）

#### 列出训练任务

```bash
python coreshub/scripts/training.py list \
  --zone xb3 \
  [--start-at "2025-01-01 00:00:00"] \
  [--end-at "2025-01-31 23:59:59"] \
  [--limit 10] [--offset 0]
```

- 时间格式：`YYYY-MM-DD HH:MM:SS`
- 默认查询最近一周内的任务

返回字段包含：`train_uuid`、`name`、`status`、`created_at` 等

#### 查看训练日志

```bash
python coreshub/scripts/training.py logs \
  --zone xb3 \
  --train-uuid <train_uuid> \
  [--start-time <纳秒时间戳>] \
  [--end-time <纳秒时间戳>] \
  [--size 100] [--reverse] [--fuzzy]
```

- `--train-uuid`：**必填**，从 `list` 命令返回的 `train_uuid` 字段获取
- 时间戳为**纳秒**精度，默认查询最近 12 小时
- 先调用 `list` 获取 `train_uuid`，再调用 `logs`

---

### 4. 推理服务（inference.py）

#### 列出推理服务

```bash
python coreshub/scripts/inference.py list \
  --zone xb3 \
  --owner <user_id> \
  [--key-words "关键字"] [--page 1] [--size 10]
```

返回字段包含：`service_id`、`name`、`status`、`endpoint` 等

#### 查看服务日志

```bash
python coreshub/scripts/inference.py logs \
  --zone xb3 \
  --owner <user_id> \
  --service-id <service_id> \
  [--start-time "2025-01-01T00:00:00.000Z"] \
  [--end-time "2025-01-02T00:00:00.000Z"] \
  [--size 100] [--reverse]
```

- `--service-id`：**必填**，从 `list` 命令返回的 `service_id` 字段获取
- 时间格式：`YYYY-MM-DDTHH:MM:SS.000Z`（UTC）
- 默认查询最近 24 小时

---

### 5. iMaaS 大模型服务（imaas.py）

#### 查看可用模型列表

```bash
python coreshub/scripts/imaas.py models \
  --zone xb3 \
  --owner <user_id> \
  [--key-words "llama"] \
  [--model-tag "txt2txt,txt2img"] \
  [--page 1] [--size 100]
```

`--model-tag` 可选值：
- `txt2txt` — 文本生成
- `txt2img` — 图片生成
- `txt2video` — 视频生成
- `img2video` — 图生视频
- `audio` — 音频处理
- `embedding` — 向量嵌入
- `rerank` — 重排序
- `crossmodel` — 跨模态

返回字段包含：`id`（如 `md-tDz8i3XJ`）、`name`、`price`（每 1k token 价格，单位人民币）等

#### 查看单个模型详情

```bash
python coreshub/scripts/imaas.py model \
  --zone xb3 \
  --owner <user_id> \
  --model-id md-tDz8i3XJ
```

- `--model-id`：**必填**，从 `models` 命令获取，格式如 `md-xxxxxx`

#### 查看 API Key 列表

```bash
python coreshub/scripts/imaas.py apikeys \
  --zone xb3 \
  --owner <user_id> \
  [--key-words "关键字"] [--page 1] [--size 10]
```

#### 查询用量统计（Token 消耗）

```bash
python coreshub/scripts/imaas.py metrics \
  --zone xb3 \
  --owner <user_id> \
  --start-time 1740000000 \
  [--end-time 1740086400] \
  [--aggr-type range] \
  [--api-key "key1,key2"] \
  [--model "gpt-4,llama3"] \
  [--token-type "input,output"] \
  [--unit "token,count"]
```

- `--start-time`：**必填**，Unix 时间戳（秒）
- `--end-time`：默认当前时间
- 时间范围限制：**1 分钟 ～ 30 天**
- `--aggr-type`：
  - `range`（推荐）— 时序折线，`result[].sum` 为区间总量
  - `sum` — 滚动增量，一般不推荐
- `--token-type`：`input` / `output` / `cached`（留空=全部）
- `--unit`：`token` / `count` / `seconds` / `words`（留空=全部）

---

## 工作流示例

### 查询账户下所有容器实例的 SSH 信息

```bash
# 步骤 1：列出已有容器实例，找到目标 uuid
python coreshub/scripts/container.py list --zone xb3

# 步骤 2：使用 uuid 获取 SSH 访问信息
python coreshub/scripts/container.py ssh --zone xb3 --uuid <从步骤1获取的uuid>
```

### 查询上周 iMaaS token 消耗汇总

```bash
# 步骤 1：查询最近 7 天的 token 用量（以当前为基准的近似时间戳）
python coreshub/scripts/imaas.py metrics \
  --zone xb3 \
  --start-time $(date -d "7 days ago" +%s) \
  --aggr-type range
```

### 查询分布式训练任务日志

```bash
# 步骤 1：获取任务列表，找到 train_uuid
python coreshub/scripts/training.py list --zone xb3

# 步骤 2：查看该任务的日志
python coreshub/scripts/training.py logs --zone xb3 --train-uuid <uuid>
```

---

## 输出格式

所有命令均输出 **JSON 格式** 到 stdout，错误信息输出到 stderr。

可配合 `jq` 进行过滤：

```bash
# 只显示模型名称列表
python coreshub/scripts/imaas.py models --zone xb3 | jq '[.list[].name]'

# 只显示容器实例 uuid 和名称
python coreshub/scripts/container.py list --zone xb3 | jq '[.items[] | {uuid, name, status}]'
```

---

## 区域配置

查看当前支持的区域：

```bash
python coreshub/scripts/epfs.py zones
# 或任意脚本的 zones 子命令
```

默认区域：`xb3`（西北3区）。如需切换，通过 `--zone` 参数指定，或设置 `CORESHUB_ZONES` 环境变量。

---

## 依赖安装

```bash
pip install requests click
```

或使用 uv：

```bash
uv pip install requests click
```
