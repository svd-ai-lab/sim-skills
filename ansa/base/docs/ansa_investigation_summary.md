# ANSA 调研与测试汇总报告

> 日期: 2026-04-03
> 状态: 阶段性汇报，等待用户反馈

---

## 一、资料来源检索

### 1. 已下载的社区项目
| 来源 | 位置 | 内容 |
|------|------|------|
| sshnuke333/ANSA-Scripts | `reference/ANSA-Scripts/` | FE_Counter, Free_Edge, Master_Slave (3个GUI工具脚本) |
| vahadruya/Skewed_Elements | `reference/Basic_Python_Script_*/` | 偏斜网格自动修复 (1个headless脚本) |
| Opel+BETA CAE论文 | `reference/ANSA_Scripting_User_Guide.md` | 行人保护仿真前处理自动化 |

### 2. ANSA安装目录官方脚本 (E:\Program Files (x86)\ANSA\ansa_v25.0.0\scripts\)

ANSA 安装目录下有 **130+ 个 .py 脚本** (RemoteControl、Mesh、CFD、Properties 等)，可在本地 ANSA 环境中作为实现参考查阅。

> **注:** 早期调查曾将部分官方脚本与 API 文档复制到 `reference/official_docs/` 和 `reference/official_scripts/`。这两个目录已在 issue #2 的 IP 合规清理中整体删除 — BETA CAE 的 API 文档与示例脚本受 EULA 约束，不能在 Apache-2.0 公共仓库中再分发。
>
> 原始内容在**已授权的本地 ANSA 安装**中可直接查阅（默认 Windows 路径 `E:\Program Files (x86)\ANSA\ansa_v25.0.0\` — 其他安装版本/位置请相应调整）：
>
> | 曾经镜像的 skill 路径 | ANSA 安装内对应位置 |
> |---|---|
> | `reference/official_docs/*.md` (11 份 API 文档) | `docs\extending\python_api\` |
> | `reference/official_scripts/RemoteControl/ansa/AnsaProcessModule.py` | `scripts\RemoteControl\ansa\AnsaProcessModule.py` |
> | `reference/official_scripts/RemoteControl/ansa_examples/` (drive_ansa.py, serve_ansa.py, exconfig.py, test_script_ansa.py, test_script_bytes_ansa.py) | `scripts\RemoteControl\ansa_examples\` |
> | `reference/official_scripts/Mesh/` (SampleProject.py, SampleBatchMesh.py) | `scripts\Mesh\` |
>
> `ansa/tests/test_runtime.py::test_official_test_script` 已经引用其中的 `test_script_ansa.py` —— 运行该测试会就地触发本地安装中的脚本，无需仓库再分发。

---

## 二、重大发现: ANSA 官方 RemoteControl (IAP)

**之前结论"ANSA没有session API"是错误的。**

ANSA 有官方的 Inter-ANSA Protocol (IAP)，实现在 `scripts/RemoteControl/ansa/AnsaProcessModule.py`：

```
启动方式: ansa_win64.exe -listenport 9999
协议: 自定义TCP二进制协议
客户端: AnsaProcessModule.py (纯Python, 不依赖ansa模块)
```

API:
```python
# 方式1: 连接到已运行的ANSA (serve_ansa.py)
connection = IAPConnection(port=9999)

# 方式2: 启动新ANSA并连接 (drive_ansa.py)  
process = AnsaProcess(ansa_command=ANSA_EXE, run_in_batch=False)
connection = process.get_iap_connection()

# 通用操作
connection.hello()                           # 握手
connection.run_script_file('script.py', 'main')  # 执行脚本文件
connection.run_script_text("print('hi')")    # 执行代码片段
connection.goodbye(PostConnectionAction.keep_listening)  # 保持监听
connection.goodbye(PostConnectionAction.shut_down)       # 关闭ANSA
```

**影响**: 这意味着ion的ANSA driver未来可以支持持久会话模式（类似Fluent/COMSOL），不必每次都冷启动。

---

## 三、License问题解决

**根因**: 两个bug叠加
1. `ansa64.bat` 默认设 `ANSA_SRV=ansa_srv.localdomain`（不可解析）
2. `ansa64.bat` 在路径含空格时环境变量拼接错误

**修复**: driver的 `_run_python()` 生成wrapper bat，直接调用 `ansa_win64.exe`，自行设置 `ANSA_SRV=localhost` + 全部环境变量。

---

## 四、已完成的测试

### 单元测试 (31个pytest, 不需要ANSA进程)
| 类别 | 测试数 | 内容 |
|------|--------|------|
| PreFlight | 5 | driver导入、名称、connect检测版本 |
| Detect | 7 | 识别.py/.ansa/.txt等文件类型 |
| Lint | 10 | 语法、import、main()、GUI函数检查 |
| ParseOutput | 5 | JSON提取、空输出、多行输出 |
| ErrorPaths | 3 | 未安装、.ansa直接运行、不支持的扩展名 |
| Execution | 1 | run_file基本执行 |

### 真实ANSA执行测试 (8个, 需要ANSA进程)

| 用例 | 脚本 | 测试内容 | 结果 | 耗时 |
|------|------|----------|------|------|
| EX-06 | ex_hello.py | ANSA启动 + JSON输出 | PASS | 1.52s |
| EX-07 | ex_create_mesh.py | CollectEntities + CreateEntity(PSHELL) | PASS | 1.45s |
| EX-08 | ex_deck_info.py | 7种solver deck可用性查询 | PASS | 1.56s |
| EX-09 | ex_quality_check.py | MAT1+PSHELL创建/读回 | PASS | 1.44s |
| EX-10 | ex_nastran_model.py | 3材料+4属性完整创建 | PASS | 1.48s |
| **EX-11** | ex_official_iap_test.py | **官方IAP test_script模式** | PASS | 1.59s |
| **EX-12** | ex_official_pshell_report.py | **官方PshellDataToText模式** | PASS | 1.66s |
| **EX-13** | ex_official_batch_mesh_info.py | **官方batchmesh API探测** | PASS | 1.42s |

---

## 五、诚实评估：还缺什么

### 缺少的关键测试（用户指出的问题）

**没有完成"读入几何体 → 生成网格"的完整流程测试。**

目前所有测试都是：
- 在空模型上创建材料/属性（不涉及几何）
- 探测API可用性（不执行实际操作）
- 运行hello world级脚本

真正有价值的测试应该是：
1. **读入一个CAD/IGES几何文件** → `base.Open()` 或 CAD翻译
2. **生成表面网格** → `batchmesh` 或 `mesh` API
3. **检查网格质量** → `base.ElementQuality()`, `base.CalculateOffElements()`
4. **导出求解器deck** → `base.OutputNastran()`
5. 输出统计JSON → sim `parse_output()` 解析

### 阻塞原因

1. **没有几何文件**: 安装目录没有找到示例 .iges 或 .ansa 模型文件
2. **官方示例都需要GUI**: `SampleBatchMesh.py` 用 `utils.SelectOpenDir` 选择目录；`SampleProject.py` 需要 .iges 文件
3. **CreateEntity("GRID")在空模型返回None**: 无法纯API创建几何

### 需要解决的问题

1. 在ANSA安装目录或其他位置找到示例几何文件（.iges, .step, .ansa）
2. 或者用ANSA API从参数创建简单几何体（如果有相关API）
3. 然后走完整个 geometry → mesh → quality → export 流程

### RemoteControl (IAP) 尚未测试

发现了官方IAP但还没有实际测试 `-listenport` 模式是否能工作。这可能是Phase 2的方向。

---

## 六、文件变更清单

### 新增文件
| 文件 | 内容 |
|------|------|
| `reference/ansa_api_reference.md` | ANSA Python API综合参考 |
| `reference/ANSA-Scripts/` | 社区开源脚本 (git clone) |
| `reference/Basic_Python_Script_*/` | 偏斜网格修复示例 (git clone) |
| `tests/fixtures/ex_hello.py` | 冒烟测试 |
| `tests/fixtures/ex_create_mesh.py` | 实体收集测试 |
| `tests/fixtures/ex_deck_info.py` | Deck查询测试 |
| `tests/fixtures/ex_quality_check.py` | 材料属性测试 |
| `tests/fixtures/ex_nastran_model.py` | 模型构建测试 |
| `tests/fixtures/ex_official_iap_test.py` | 官方IAP模式测试 |
| `tests/fixtures/ex_official_pshell_report.py` | 官方属性报告模式测试 |
| `tests/fixtures/ex_official_batch_mesh_info.py` | 官方batchmesh API测试 |
| `docs/ansa_investigation_summary.md` | 本文档 |

### 修改文件
| 文件 | 变更 |
|------|------|
| `sim/src/sim/drivers/ansa/driver.py` | `_run_python()` 直接调用exe + ANSA_SRV=localhost |
| `sim/src/sim/drivers/__init__.py` | 注册AnsaDriver到DRIVERS列表 |
| `skills/ansa-sim/SKILL.md` | 新增API速查表、测试脚本列表、IAP发现 |
| `skills/ansa-sim/known_issues.md` | ISSUE-001已解决、新增ISSUE-002/003 |
| `skills/ansa-sim/tests/execution_test_cases_v1.md` | EX-06~EX-13全部PASS |

---

## 七、下一步建议

1. **找到或创建示例几何文件**，完成"读入几何 → 网格生成 → 质量检查 → 导出"完整流程
2. **测试IAP远程控制** (`-listenport` 模式)，评估是否可作为Phase 2的session方案
3. 如果IAP可行，设计 `connect/exec/disconnect` 生命周期（类似Fluent driver）
