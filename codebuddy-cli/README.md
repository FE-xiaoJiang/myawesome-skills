# CodeBuddy CLI 执行技能

## 概述

通过 CodeBuddy CLI（`codebuddy` 命令行）执行用户指令的技能。支持非交互模式调用、超时处理、任务拆分策略，可无缝接入 CodeBuddy AI 能力完成代码分析、自动化脚本、日常问答等任务。

## 触发关键词

当用户提到以下任一关键词时触发本技能：

- "用 cb 执行"、"cb -p"
- "用 codebuddy cli"、"codebuddy -p"
- "用 cb 来做"、"让 cb 帮忙"
- "用 cb 继续"、"cb 继续往下"

## 前置要求

1. **安装 CodeBuddy CLI**：确保 `codebuddy` 命令在 PATH 中可用
2. **Node.js 版本**：需要 Node.js v18.20.8+（建议通过 nvm 管理）
3. **登录状态**：首次使用需在终端执行 `codebuddy` 进入交互模式完成 iOA 登录

## 核心命令模板

```bash
source ~/.nvm/nvm.sh && nvm use default 2>/dev/null && cd <工作目录> && codebuddy -p "<prompt>" -y --dangerously-skip-permissions --mcp-config '{"mcpServers":{}}' --strict-mcp-config 2>&1 | tail -<行数>
```

### 参数说明

| 参数 | 用途 | 必需 |
|------|------|:----:|
| `source ~/.nvm/nvm.sh && nvm use default` | 加载 nvm 并切换到默认 Node.js 版本 | ✅ |
| `-p "<prompt>"` | 非交互模式，打印输出后退出 | ✅ |
| `-y` / `--dangerously-skip-permissions` | 跳过所有权限检查，自动确认文件编辑等操作 | ✅ |
| `--mcp-config '{"mcpServers":{}}'` | 传入空 MCP 配置，避免 MCP 初始化失败 | ✅ |
| `--strict-mcp-config` | 只使用 `--mcp-config` 指定的配置，忽略其他 MCP 配置 | ✅ |
| `2>&1 \| tail -<行数>` | 合并 stderr 并截取尾部输出（避免输出过长） | ✅ |

### 可选增强参数

| 参数 | 用途 | 场景 |
|------|------|------|
| `--model <model>` | 指定模型 | 用户要求使用特定模型时 |
| `--max-turns <N>` | 限制 agentic 轮次 | 控制执行深度 |
| `-c` / `--continue` | 继续上一次对话 | 需要延续上下文时 |

## 执行策略

### 1. 任务粒度控制

CodeBuddy CLI 有执行超时限制。**必须将大任务拆分为小任务**：

- ❌ 不要一次让 CodeBuddy 执行整个里程碑（如 "完成 M1 所有 4 个功能点"）
- ✅ 每次只执行 1-2 个功能点（如 "完成 F-M1-001 数据库初始化"）
- ✅ 如果超时，进一步拆分任务粒度

### 2. 输出截取策略

根据任务复杂度调整 `tail` 行数：

- 简单任务（编译检查、状态查询）：`tail -80`
- 中等任务（单个模块实现）：`tail -100` ~ `tail -120`
- 复杂任务（评审、多文件生成）：`tail -150` ~ `tail -200`

### 3. Prompt 编写规范

- 明确指定工作目录路径
- 列出具体要做的事项（编号列表）
- 包含验证步骤（如 "确保编译通过"、"运行测试"）
- 提供必要的环境上下文（如 "本机 PostgreSQL 在 localhost:5432 已运行"）

### 4. 错误处理

| 错误 | 处理方式 |
|------|---------|
| 执行超时 | 拆分为更小的子任务重试 |
| "Server not initialized" | 确认已加 `--mcp-config` 和 `--strict-mcp-config` |
| Node.js 版本不兼容 | 确认已加 `source ~/.nvm/nvm.sh && nvm use default` |
| 网络不通 | 检查 `curl -sI https://copilot.tencent.com` 连通性 |
| 未登录 | 提示用户在终端执行 `codebuddy` 进入交互模式完成 iOA 登录 |

### 5. 串行执行

每次只执行一条 codebuddy 命令，等前一个完成后根据输出结果决定下一步。不要并行执行多条 codebuddy 命令。

## 使用示例

### 示例 1：执行单个功能点

```bash
source ~/.nvm/nvm.sh && nvm use default 2>/dev/null && cd /path/to/project && codebuddy -p "请完成数据库初始化。本机 PostgreSQL 16 在 localhost:5432 已运行。请：
1. 用 psql 创建数据库 audiobook_dev
2. 创建 .env 文件配置 DATABASE_URL
3. 执行 prisma migrate dev 生成表结构
请完整执行并报告结果。" -y --dangerously-skip-permissions --mcp-config '{"mcpServers":{}}' --strict-mcp-config 2>&1 | tail -100
```

### 示例 2：代码评审

```bash
source ~/.nvm/nvm.sh && nvm use default 2>/dev/null && cd /path/to/project && codebuddy -p "请评审 src/auth/ 目录下的代码，检查安全性和最佳实践。" -y --dangerously-skip-permissions --mcp-config '{"mcpServers":{}}' --strict-mcp-config 2>&1 | tail -150
```

### 示例 3：生成单元测试

```bash
source ~/.nvm/nvm.sh && nvm use default 2>/dev/null && cd /path/to/project && codebuddy -p "为 src/utils/parser.ts 中的所有函数生成 jest 单元测试，覆盖正常和异常分支。" -y --dangerously-skip-permissions --mcp-config '{"mcpServers":{}}' --strict-mcp-config --timeout 300 2>&1 | tail -120
```

## SKILL.md 说明

完整的 Knot Skill 定义文件（`SKILL.md`）位于本目录的 `scripts/SKILL.md`，供 Knot 平台加载使用。

## 许可证

MIT License

## 开发者

- GitHub: https://github.com/FE-xiaoJiang/myawesome-skills
- 技能目录: /codebuddy-cli/

## 更新日志

- v1.0.0: 初始版本发布
  - 非交互模式调用规范
  - 超时处理与任务拆分策略
  - 完整错误处理指南
  - 多场景使用示例
