# CFX Session Workflow — Interactive Post-Processing

## Architecture Overview

CFX session 采用三阶段混合架构，求解只执行一次：

```
Phase 1: cfx5solve -batch -def file.def    ← 求解（一次，~6分钟）
              ↓ 生成 .res 文件
Phase 2: cfx5post -line file.res           ← 常驻进程，交互查询（毫秒级）
              ↓ agent 要出图时
Phase 3: cfx5post -batch _render.cse       ← 临时进程，渲染出图（~5秒）
```

**关键点**：Phase 3 只重放可视化 CCL（CONTOUR、HARDCOPY），不重新求解。`.res` 里的数据是现成的，渲染只是读取和展示。

## cfx5post -line 交互协议

启动后显示 `CFX>` 提示符，接受以下命令：

| 命令 | 缩写 | 用途 | 示例 |
|------|------|------|------|
| `enterccl` | `e` | 进入 CCL 输入模式 | 输入后逐行写 CCL，`.e` 提交，`.c` 取消 |
| `getstate` | `s` | 查询对象列表/状态 | `s` 列出全部，`s CONTOUR:P` 查特定对象 |
| `delete` | `d` | 删除对象 | `d CONTOUR:P` |
| `help` | `h` | 帮助 | |
| `quit` | `q` | 退出 | |
| `calculate` | `calc` | 内置计算器 | `calc area, inlet` |
| `!` | - | 执行 Perl | `! print 'hello'.chr(10);` |
| `readsession` | `rs` | 加载 .cse 文件 | `rs filename=post.cse` |

### enterccl 模式

```
CFX> e
When done, type '.e' to process or '.c' to cancel:
CONTOUR: PressureField
  Colour Variable = Pressure
  ...
END
.e                    ← 提交执行
```

**注意**：不能在 `CFX>` 提示符直接写 CCL（会报 "Action XXX is not recognized"）。必须先 `e` 进入 CCL 模式。

## 数值查询：Perl evaluate()

这是获取精确物理量的唯一可靠方式。语法：

```
! ($v,$u) = evaluate('表达式'.chr(64).'位置'); print 'RESULT: '.$v.' ['.$u.']'.chr(10);
```

**为什么用 `chr(64)` 而不是 `@`**：Perl 中 `@` 是数组前缀，`@inlet` 会被解析为数组变量。`chr(64)` 是 `@` 的 ASCII 码，避免 Perl 解析冲突。

### 常用表达式

| 查询 | 表达式 | 示例结果 |
|------|--------|---------|
| 质量流量 | `massFlow()@inlet` | 1.379 [kg s^-1] |
| 面积平均压力 | `areaAve(Pressure)@outlet` | -0.058 [Pa] |
| 面积平均速度 | `areaAve(Velocity)@inlet` | 0.931 [m s^-1] |
| 最大值 | `maxVal(Pressure)@Default Domain` | 2213.9 [Pa] |
| 最小值 | `minVal(Pressure)@Default Domain` | -3304.3 [Pa] |
| 面积 | `area()@inlet` | 0.00166 [m^2] |
| 体积积分 | `volumeInt(Density)@Default Domain` | ... |
| 质量流量加权平均 | `massFlowAve(Temperature)@outlet` | ... |

### 可用函数完整列表

```
area, areaAve, areaInt, ave, count, countTrue, force, forceNorm,
length, lengthAve, lengthInt, lineCloudAve, massFlow, massFlowAve,
massFlowAveAbs, massFlowInt, maxVal, minVal, probe, sum, torque,
volume, volumeAve, volumeInt
```

## 图像渲染：Hybrid 方案

### 问题

`cfx5post -line` 在 headless 模式下无法渲染填充面（contour 只有线框，没有颜色）。这是 CFX 的 software renderer 限制。

### 解决方案

Driver 自动采用 hybrid 模式：
1. agent 通过 `-line` session 发送 CONTOUR 定义 → driver 记录到 CCL history
2. agent 请求导出图像（HARDCOPY + >print）→ driver 拦截
3. driver 将 CCL history 重放到临时 `.cse` 文件
4. driver 调用 `cfx5post -batch _render.cse results.res` → 正确渲染
5. 临时 `.cse` 自动删除

**对 agent 完全透明**——同一个 `run()` 接口，HARDCOPY 请求自动走 hybrid 路径。

### 示例工作流

```python
# Step 1: 创建 contour（在 -line session 中执行，记录到 history）
driver.run("""CONTOUR: P
  Colour Variable = Pressure
  Contour Range = Global
  Domain List = All Domains
  Fringe Fill = On
  Location List = Default Domain Default, inlet, outlet
  Number of Contours = 20
  Surface Drawing = Smooth Shading
  Visibility = On
END""")

# Step 2: 导出图像（自动走 hybrid batch 渲染）
driver.run("""HARDCOPY:
  Hardcopy Filename = /path/to/output.png
  Hardcopy Format = png
  Image Height = 1200
  Image Width = 1600
  White Background = On
END
>print""")
# → 实际生成带颜色填充的云图，不是线框

# Step 3: 修改变量（追加到 history）
driver.run("""CONTOUR: P
  Colour Variable = Velocity
END""")

# Step 4: 再次导出（history 包含两段 CONTOUR CCL，batch 重放后得到速度云图）
driver.run("""HARDCOPY:
  Hardcopy Filename = /path/to/velocity.png
  ...
END
>print""")
```

## 质量守恒验证模式

session 最有价值的用法是分步验证物理量：

```python
# 入口质量流量
r1 = driver.run("evaluate(massFlow()@inlet)")
# → 1.379 kg/s（与 CCL 设定一致 ✓）

# 出口质量流量
r2 = driver.run("evaluate(massFlow()@outlet)")
# → -1.379 kg/s（负号=流出方向，绝对值一致 = 质量守恒 ✓）

# 压降
r3 = driver.run("evaluate(areaAve(Pressure)@inlet)")
r4 = driver.run("evaluate(areaAve(Pressure)@outlet)")
# → inlet 1866 Pa, outlet ~0 Pa → 压降 1866 Pa ✓

# 速度连续性：Q = m_dot / (rho * A)
# 1.379 / (894 * 0.00166) ≈ 0.93 m/s
r5 = driver.run("evaluate(areaAve(Velocity)@inlet)")
# → 0.931 m/s ✓
```

## 已知限制

1. **-line 启动慢**：加载 .res 需要 ~15 秒（大文件更久）
2. **-line 不能渲染**：填充面只有线框（已通过 hybrid 方案解决）
3. **Perl 字符串转义**：`@` 必须用 `chr(64)`，双引号建议用单引号替代
4. **CCL 必须通过 enterccl**：不能在 `CFX>` 直接写 CCL 关键字
5. **calc 命令输出不在 stdout**：数值在 progress bar 里，用 Perl evaluate 替代
