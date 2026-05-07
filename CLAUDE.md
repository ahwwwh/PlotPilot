<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **PlotPilot** (5655 symbols, 16625 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/PlotPilot/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/PlotPilot/context` | Codebase overview, check index freshness |
| `gitnexus://repo/PlotPilot/clusters` | All functional areas |
| `gitnexus://repo/PlotPilot/processes` | All execution flows |
| `gitnexus://repo/PlotPilot/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

- Re-index: `npx gitnexus analyze`
- Check freshness: `npx gitnexus status`
- Generate docs: `npx gitnexus wiki`

<!-- gitnexus:end -->

---

# 上游合并 SOP — 不允许打破的本地扩展

本仓库 fork 自 `shenminglinyi/PlotPilot`，本地维护一组**关键扩展功能**。上游合并必须按本流程执行，违反任何一步 = 3.25。

## 本地扩展清单（保护名单）

合并前必须知道这些文件由我们独立维护，上游变更要逐行核对：

| 文件 | 维护原因 | 关键 commit |
|------|---------|------------|
| `infrastructure/ai/providers/claude_cli_provider.py` | keychain OAuth 注入 | f897b5b, 54e9a43 |
| `infrastructure/ai/providers/gemini_cli_provider.py` | 7897 代理 + NODE_TLS bypass | f897b5b, 54e9a43 |
| `infrastructure/ai/providers/__init__.py` | CLI provider 按需 import | f897b5b |
| `infrastructure/ai/provider_factory.py` | claude-cli/gemini-cli 路由 | f897b5b |
| `infrastructure/persistence/database/connection.py` | execute_write 应用层重试 | b8f2bec |
| `infrastructure/persistence/database/sqlite_chapter_repository.py` | 用 execute_write | b8f2bec |
| `infrastructure/persistence/database/sqlite_novel_repository.py` | 用 execute_write | b8f2bec |
| `infrastructure/persistence/database/story_node_repository.py` | _get_connection 加 WAL+busy_timeout | bb3aef1 |
| `application/engine/services/autopilot_daemon.py` | 真并发 + 幕号漂移降级 | 68b61c8, 76d1094 |
| `application/ai/llm_control_service.py` | LLMProtocol 扩展支持 cli | 1205a4a |
| `interfaces/api/v1/workbench/llm_control.py` | _fetch_cli_models + 模型兜底 | 54e9a43 |
| `infrastructure/persistence/database/schema.sql` | protocol CHECK 含 claude-cli/gemini-cli | 1205a4a |

## 合并前

```bash
# 1. fetch 上游
git fetch upstream

# 2. 列出潜在冲突文件（保护名单 ∩ 上游改动）
git diff --name-only HEAD upstream/master | grep -F -f <(echo "
infrastructure/ai/providers/claude_cli_provider.py
infrastructure/ai/providers/gemini_cli_provider.py
infrastructure/ai/providers/__init__.py
infrastructure/ai/provider_factory.py
infrastructure/persistence/database/connection.py
infrastructure/persistence/database/sqlite_chapter_repository.py
infrastructure/persistence/database/sqlite_novel_repository.py
infrastructure/persistence/database/story_node_repository.py
application/engine/services/autopilot_daemon.py
application/ai/llm_control_service.py
interfaces/api/v1/workbench/llm_control.py
infrastructure/persistence/database/schema.sql
")

# 3. 备份关键 patch 防丢
mkdir -p /tmp/plotpilot-backup-$(date +%s)
git format-patch upstream/master..HEAD -o /tmp/plotpilot-backup-*/

# 4. 备份 .git（防 fetch 包损坏）
cp -R .git /tmp/plotpilot-backup-*/git.backup
```

## 合并

```bash
git merge upstream/master --no-edit
# 有冲突：保留名单内文件的本地实现，集成上游其他改动
```

## 合并后回归验收（缺一不可）

```bash
# 1. CLI provider 单元测试 16/16 必须绿
.venv/bin/python -m pytest tests/unit/infrastructure/ai/providers/test_claude_cli_provider.py \
                            tests/unit/infrastructure/ai/providers/test_gemini_cli_provider.py -v
# 2. 并发设置测试
.venv/bin/python -m pytest tests/unit/infrastructure/persistence/database/test_story_node_repository_concurrency.py -v

# 3. 完整重启 backend（uvicorn --reload 不会重载 daemon spawn 子进程）
lsof -ti :8005 | xargs kill -9; pgrep -f "multiprocessing.spawn" | xargs kill -9
.venv/bin/uvicorn interfaces.main:app --host 0.0.0.0 --port 8005 > logs/backend.log 2>&1 &
sleep 5

# 4. 实测两本并发写作
curl -sX POST localhost:8005/api/v1/autopilot/<novel-id-A>/start -H 'content-type: application/json' -d '{}'
curl -sX POST localhost:8005/api/v1/autopilot/<novel-id-B>/start -H 'content-type: application/json' -d '{}'
sleep 120
# 验收信号：日志中两本小说在同一秒"开始写作"，节拍 1/4 在 1-5 秒内并发完成，无 "database is locked"
grep -E "开始写作|节拍.*完成|locked" logs/aitext.log | tail -30

# 5. 测试 claude-cli /test 接口
curl -sX POST localhost:8005/api/v1/llm-control/test -H 'content-type: application/json' \
  -d '{"id":"claude-cli","name":"Claude CLI","protocol":"claude-cli","base_url":"","api_key":"","model":"claude-sonnet-4-6","temperature":0,"max_tokens":64,"timeout_ms":120000,"extra_params":{}}'
# 期望：{"ok":true, "preview":"连接成功"}
```

**所有 5 步通过 → 才允许 push origin master**。

## 红线

- ❌ 直接 `git merge upstream/master` 后立刻 push（没跑回归 = 自嗨）
- ❌ 看到保护名单文件冲突就取上游版本（会丢本地修复）
- ❌ 用 `--reload` 验证（daemon 子进程跑老代码）
- ❌ 只看 `/test` 接口绿就放过（必须实测两本并发 AI 托管）

