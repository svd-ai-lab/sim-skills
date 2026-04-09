# ANSA Runtime 开发报告

> 日期: 2026-04-03
> 最终结果: **48/48 测试全部通过**

---

## 做了什么

从零搭建了 ANSA driver 的 Phase 2 持久会话 runtime，并补齐了真实前处理流程测试。

### 时间线

1. **调研 ANSA 官方脚本** — 在安装目录 `scripts/` 发现 130+ 个官方 Python 脚本
2. **发现 IAP 远程控制** — `scripts/RemoteControl/` 包含官方 Inter-ANSA Protocol，**推翻了之前"ANSA 没有 session API"的结论**
3. **验证 IAP 可用** — 8/8 步骤全部通过：launch → connect → hello → run_script_text → run_script_file → goodbye
4. **实现 runtime** — 按照 Fluent driver 的 schemas+runtime+driver 模式实现
5. **修复 subprocess.PIPE 导致 ANSA 崩溃的问题** — 改用 DEVNULL
6. **修复 IAP 初始化时序问题** — 端口打开后加 1s 延迟等待 IAP 协议栈就绪
7. **补齐 pipeline 测试** — Read Nastran → Quality Check → Modify → Export

---

## 关键发现: ANSA 官方 IAP (Inter-ANSA Protocol)

位于 `scripts/RemoteControl/ansa/AnsaProcessModule.py`，纯 Python stdlib（socket+struct），零外部依赖。

```
启动:    ansa_win64.exe -nolauncher -listenport <port> -foregr -nogui
连接:    IAPConnection(port) → TCP socket
握手:    hello() → HelloResponse
执行:    run_script_text(code, "main", keep_database)
         run_script_file(path, "main", keep_database)
返回值:  string_dict {"key": "value"} 或 bytes (pickle)
断开:    goodbye(shut_down | keep_listening)
```

关键特性:
- `keep_database` 模式下**状态跨调用持久化**（前一步创建的实体后续可见）
- 启动约 2 秒，单次 snippet 执行约 0.1-0.3 秒
- `keep_listening` 模式允许断开后重连

---

## 新增文件

### sim driver 层 (`sim/src/sim/drivers/ansa/`)

| 文件 | 行数 | 内容 |
|------|------|------|
| `schemas.py` | 60 | `SessionInfo` + `RunRecord` 数据类，与 Fluent driver 对齐 |
| `runtime.py` | 240 | `AnsaRuntime` — IAP 生命周期管理（launch/connect/exec_snippet/exec_file/disconnect） |

### 修改文件

| 文件 | 变更 |
|------|------|
| `driver.py` | 新增 `launch()`, `run()`, `run_script()`, `disconnect()`, `is_connected`；Phase 1 `run_file()` 完全保留 |
| `__init__.py` | 导出 `SessionInfo`, `RunRecord` |

### 测试文件 (`sim-agent-ansa/tests/`)

| 文件 | 测试数 | 内容 |
|------|--------|------|
| `test_runtime.py` | 12 | IAP session 生命周期 + snippet 执行 + 状态持久化 + 错误处理 |
| `test_pipeline.py` | 5 | 完整前处理流程: Read → Quality → Modify → Export |

### 测试输入文件

| 文件 | 内容 |
|------|------|
| `tests/fixtures/geometry/input_plate.nas` | 5×5 CQUAD4 平板模型 (25 节点, 16 单元, MAT1+PSHELL) |
| `tests/fixtures/geometry/test.iges` | IGES 几何文件 (从本机找到，3 个 FACE) |

---

## 架构

```
AnsaDriver
├── Phase 1: run_file(script.py)
│   └── Popen(ansa_win64.exe -execscript "script.py|main()" -nogui)
│   └── 一次性冷启动，~1.5s，适合独立脚本
│
└── Phase 2: launch() → run(code) → disconnect()
    └── Popen(ansa_win64.exe -nolauncher -listenport <port> -foregr -nogui)
    └── IAPConnection(port).hello()
    └── run_script_text(code, "main", keep_database)  ← 状态持久化
    └── goodbye(shut_down)
    └── 长期会话，首次启动 ~2s，后续 snippet ~0.1s
```

### 与 Fluent/COMSOL 对比

| 方面 | Fluent | COMSOL | ANSA |
|------|--------|--------|------|
| 协议 | gRPC (protobuf) | JPype (Java 方法调用) | IAP (自定义 TCP 二进制) |
| 外部依赖 | ansys-fluent-core | jpype + JVM | **无** (纯 stdlib) |
| 启动时间 | ~15s | ~10s | **~2s** |
| Namespace 注入 | session/solver/meshing | model/ModelUtil | **无**（脚本自行 import ansa） |
| 返回值 | Python 对象 | Java 对象 | string_dict 或 bytes |
| 日志写入 | .sim/runs/uuid.json | 无自动写入 | .sim/runs/uuid.json |

---

## 测试结果明细

### test_ansa_driver.py — 31 PASS (Phase 1)

| 类别 | 数量 | 内容 |
|------|------|------|
| PreFlight | 5 | driver 导入、名称、connect 检测版本 |
| Detect | 7 | .py/.ansa/.txt 等文件识别 |
| Lint | 10 | 语法、import、main()、GUI 函数 |
| ParseOutput | 5 | JSON 提取 |
| ErrorPaths | 3 | 未安装/不支持扩展名 |
| Execution | 1 | run_file 真实执行 |

### test_runtime.py — 12 PASS (Phase 2 IAP)

| 测试 | 内容 |
|------|------|
| test_driver_has_runtime_methods | launch/run/disconnect 方法存在 |
| test_connect_still_works | Phase 1 connect() 未受影响 |
| test_launch_returns_session_info | session_id, mode="batch", port |
| test_is_connected_after_launch | is_connected == True |
| test_simple_return_dict | `return {'hello': 'world'}` → 正确捕获 |
| test_ansa_api_create_material | CreateEntity(MAT1) 在 session 中成功 |
| test_ansa_api_state_persists | **前一步创建的 RuntimeSteel 材料在后续调用中可见** |
| test_multi_deck_query | 7 种 solver deck 全部可用 |
| test_error_in_snippet_returns_ok_false | ValueError 正确捕获，ok=False |
| test_run_record_has_timing | ended_at > started_at |
| test_official_test_script | 官方 test_script_ansa.py 返回 {'A':'0','B':'1','C':'2'} |
| test_disconnect_cleans_up | disconnect 后 is_connected=False |

### test_pipeline.py — 5 PASS (真实前处理流程)

| 步骤 | 测试 | 验证内容 |
|------|------|----------|
| **Read** | test_read_plate_model | InputNastran → 25 GRID + 16 CQUAD4 + 1 MAT1 + 1 PSHELL |
| **Quality** | test_quality_metrics | CollectEntities 确认 16 个单元完整存在 |
| **Modify** | test_add_material_and_change_thickness | 新增 Aluminum 材料 + 板厚 2mm→3mm **跨调用持久** |
| **Export** | test_export_nastran | OutputNastran → 3574 字节，包含 CQUAD4+GRID+PSHELL |
| **Verify** | test_exported_file_is_valid | 文件包含 BEGIN BULK/ENDDATA，≥16 CQUAD4 + ≥25 GRID |

---

## 修复的 Bug

| Bug | 原因 | 修复 |
|-----|------|------|
| ANSA listener 启动后 hello() 连接被断开 | `subprocess.Popen(stdout=PIPE)` 导致 ANSA stdout 缓冲区满后进程挂起 | 改用 `stdout=DEVNULL` |
| pytest 环境下 IAP hello() 失败 | 端口打开后 IAP 协议栈尚未初始化完成 | `_wait_for_port` 后加 1s 延迟 |
| IAP string_dict 不支持 float 值 | IAP 返回值只能是 `{str: str}` 字典 | 所有返回值用 `str()` 包装 |

---

## 总计

```
48 tests passed in 8.84s
├── 31 Phase 1 (one-shot batch)
├── 12 Phase 2 (IAP persistent session)
└──  5 Pipeline (Read → Quality → Modify → Export)
```
