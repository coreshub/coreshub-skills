# CoreshHub Skills

基石智算（CoreshHub）平台的 AI 编程助手 **Skills** 集合。

Skills 是供 AI 编程助手（如 Claude/Cursor/Antigravity）使用的能力包，每个 skill 包含：
- **SKILL.md**：告诉 AI 如何使用该 skill 的说明文档
- **scripts/**：AI 调用的 CLI 可执行脚本

---

## 可用 Skills

### [`coreshub/`](./coreshub/)

查询和管理基石智算平台资源，功能与 [coreshub-mcp-server](https://github.com/coreshub/mcp-server-coreshub) 完全一致，以 CLI 形式提供。

| 脚本 | 功能 |
|------|------|
| `epfs.py` | EPFS 弹性并行文件系统（列表、账单） |
| `container.py` | 容器实例 Notebook（列表、SSH 信息） |
| `training.py` | 分布式训练任务（列表、日志） |
| `inference.py` | 推理服务（列表、日志） |
| `imaas.py` | iMaaS 大模型服务（模型列表、模型详情、API Key、用量统计） |

---

## 快速开始

### 1. 配置环境变量

```bash
export QY_ACCESS_KEY_ID="<基石智算 Access Key>"
export QY_SECRET_ACCESS_KEY="<基石智算 Secret Key>"
export CORESHUB_USER_ID="<基石智算账户 ID>"
```

### 2. 安装依赖

```bash
pip install requests click
```

### 3. 运行

```bash
# 查看容器实例
python coreshub/scripts/container.py list --zone xb3

# 查看 iMaaS 模型列表
python coreshub/scripts/imaas.py models --zone xb3

# 查看帮助
python coreshub/scripts/imaas.py --help
python coreshub/scripts/imaas.py metrics --help
```

---

## Skill vs MCP Server

| 维度 | MCP Server | Skill（本项目） |
|------|-----------|--------------|
| 调用方式 | LLM 通过 MCP 协议自动调用 | AI 读取 SKILL.md 后执行 CLI 脚本 |
| 运行时 | 常驻后台进程 | 按需一次性执行 |
| 部署要求 | 需要配置 MCP Client | 仅需 Python + pip |
| 适合场景 | 生产环境/多用户 | 开发辅助/本地调试/CI 自动化 |

---

## 如何添加新 Skill

1. 在根目录创建新文件夹 `<skill-name>/`
2. 创建 `SKILL.md`（必须），包含 YAML frontmatter：
   ```markdown
   ---
   name: skill-name
   description: 简短描述这个 skill 能做什么
   ---
   # 详细说明...
   ```
3. 在 `scripts/` 目录中添加 CLI 脚本
4. 在 `scripts/requirements.txt` 中列出依赖

---

## 项目结构

```
coreshub-skills/
├── README.md
└── coreshub/                  # CoreshHub 平台资源管理 skill
    ├── SKILL.md               # AI 使用说明（核心）
    └── scripts/               # CLI 脚本
        ├── requirements.txt   # 依赖声明
        ├── epfs.py            # EPFS 文件系统
        ├── container.py       # 容器实例
        ├── training.py        # 分布式训练
        ├── inference.py       # 推理服务
        ├── imaas.py           # iMaaS 大模型服务
        └── utils/
            ├── settings.py    # 认证配置
            ├── signature.py   # API 签名工具
            └── zones.py       # 区域配置工具
```