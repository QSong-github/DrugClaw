<p align="center">
  <img src="./support/DrugClaw_Logo.png" alt="DrugClaw Logo" width="520" />
</p>

<p align="center">
  <strong>面向药物知识检索、推理与证据综合的 Agentic RAG 系统</strong>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2606.01434">📄 论文 (arXiv)</a>
  ·
  <a href="./README.md">English Version</a>
</p>

<p align="center">
  <em>资源包将在论文录用后释出。</em>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2606.01434"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2606.01434-b31b1b"></a>
  <img alt="Domain" src="https://img.shields.io/badge/Domain-Drug%20Intelligence-1f6feb">
  <img alt="Registry" src="https://img.shields.io/badge/Registry-Source%20of%20Truth-0a7f5a">
  <img alt="Skills" src="https://img.shields.io/badge/Skills-Registry%20Driven-f59e0b">
  <img alt="Modes" src="https://img.shields.io/badge/Modes-GRAPH%20%7C%20SIMPLE%20%7C%20WEB__ONLY-7c3aed">
</p>

DrugClaw 是一个面向药物问题的 CLI 与 agent runtime，强调基于证据的检索、推理、来源归因与可追溯性，而不是只生成看起来流畅的文本。

## 为什么是 DrugClaw

- 不是通用聊天助手，而是围绕靶点、适应症、重定位、安全性、DDI、PGx 和说明书信息这些真实药物问题设计
- 不只给结论，还尽量给出结构化证据和来源归因
- 既能用最小模式快速跑通，也能切到更深入、更全面的全量本地资源模式

## 5 分钟上手

如果你是第一次使用，按下面步骤走，一般就可以直接跑起来。

### 1. 克隆仓库并进入目录

```bash
git clone https://anonymous.4open.science/r/DrugClaw-01A3
cd DrugClaw
```

### 2. 安装依赖

```bash
pip install -e .
```

### 3. 准备 `api_keys.json`

DrugClaw 默认会读取仓库根目录下的 `api_keys.json`。如果你不想额外传 `--key-file`，就直接把配置文件放在仓库根目录。

请新建这个文件，并至少填写以下字段：

```json
{
  "api_key": "<your-api-key>",
  "base_url": "<your-base-url>",
  "model": "gpt-5-mini"
}
```

如果你的配置文件不在仓库根目录，后续命令请显式传 `--key-file <path>`。

### 4. 检查配置是否可用

```bash
python -m drugclaw doctor
```

如果配置和环境都正常，你应该看到类似结果：

```text
Doctor result: setup looks usable.
```

### 5. 运行第一条查询

```bash
python -m drugclaw run --query "What are the known drug targets of imatinib?"
```

如果这一步能跑通，你就已经完成了最小可用启动。

## DrugClaw 适合什么问题

- 药物靶点与机制
- 适应症与重定位证据
- 安全性与严重不良反应
- 药物相互作用
- 药物基因组学
- 说明书与临床用药信息

## 常用命令

```bash
python -m drugclaw run --query "What pharmacogenomic factors affect clopidogrel efficacy and safety?"
python -m drugclaw run --query "What are the clinically important drug-drug interactions of warfarin?"
python -m drugclaw list
```

## 两种使用模式

### 最小模式

默认就是最小模式。

仓库当前只跟踪一个最小的 `resources_metadata/` 子树，足够支持 CLI、基础查询和默认测试。对大多数新用户来说，这就是推荐起点。

适合你如果：

- 只是想快速体验 DrugClaw
- 想先跑基础查询
- 不想先下载大体积资源包

### 全量模式

如果你需要更深入、更全面的本地证据覆盖，全量资源包 `resources_metadata_full.tar.gz` 将在论文录用后释出。释出后，在仓库根目录解压：

```bash
tar -xzf resources_metadata_full.tar.gz
```

推荐顺序是（待资源包释出后）：

1. 下载 `resources_metadata_full.tar.gz`
2. 在仓库根目录解压到当前目录
3. 再次运行 `python -m drugclaw doctor`

这不是简单的数据增强包，而是在同一个 `resources_metadata/` 目录上扩展更多本地资源，让更多 `LOCAL_FILE` 资源进入可用状态，并支持更完整的本地证据查询。

适合你如果：

- 需要更高的本地资源覆盖
- 想启用更多本地资源
- 想做更深入的资源级分析或验证

## 如果你接下来想做什么

- 看可用资源和推荐入口：

```bash
python -m drugclaw list
```

- 再次检查环境：

```bash
python -m drugclaw doctor
```

- 浏览内置演示流：

```bash
python -m drugclaw demo
```

# 引用
如果本项目对你的研究有帮助，请引用：
```
Wang Q, Li B, Liang J, Shi D, Zhang B, Song Q. DrugClaw and DrugAudit: A primary-source-grounded agent and authority-aware benchmark for drug-information question answering. arXiv. 2026; arXiv:2606.01434. https://arxiv.org/abs/2606.01434

```

## 进一步阅读

- 仓库结构说明：`docs/repository-guide.md`
- 维护者说明：`maintainers/README.md`
