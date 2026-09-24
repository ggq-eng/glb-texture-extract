# glb-texture-extract

> **分类**：原创 / AI 打磨 ｜ **文件数**：10 ｜ **仓库目录**：`glb-texture-extract`

## 📌 简介

**GLB（glTF Binary）模型解包与贴图提取工具**，7 个 Python 脚本覆盖一次完整的排查过程：

解析 glTF 场景图 → 遍历节点与网格 → 找到纹理与材质的对应关系 →
导出**原始内嵌贴图**（不重采样）→ 生成「零光照纯原色」对照渲染 →
把 ORM 三通道拆开看 → 最后拼一张带中文标注的贴图总览图。

> ⚠️ 本仓库**只含工具代码**，不含任何第三方模型与贴图素材 —— 素材版权归原作者，请自备。

## 🎯 适用场景

- 拿到一个 `.glb` 模型，需要**取出里面的贴图**（而不只是截图）
- 检查材质通道到底有没有正确打包（`baseColor` / `normal` / `metallicRoughness` / `ORM`）
- 需要**多视角预览图**（正面 / 侧面 / 背面 / 底部）做交付或汇报
- 排查「模型在查看器里发黑 / 发灰」这类问题——通常就是 ORM 通道接错了

## ✨ 功能特性

- **场景图遍历**：`walk()` 递归走节点树，理清 mesh → primitive → material → texture 的引用链
- **原始贴图导出**：`export_original.py` 导出 GLB 内嵌的**原始贴图字节**（不做重采样，不糊）
- **零光照对照渲染**：同一模型渲一版「无光照、纯原色」的图，用来区分「贴图本身暗」还是「光照算暗」
- **ORM 通道拆解**：`explain_atlas.py` 把 `metallicRoughness` 贴图的 R/G/B 三个通道拆开看
  （R = Ambient Occlusion / G = Roughness / B = Metallic）
- **多视角渲染**：`build_cache.py` / `analyze2.py` 输出正面 / 侧面 / 背面 / 底部多张视图
- **带中文标注的总览图**：`make_tex_sheet.py` 自选 CJK 字体，把各贴图与通道拼成一张说明图

## 📦 环境要求

| 项 | 要求 |
|---|---|
| Python | 3.9+ |
| 依赖 | `pygltflib`（glTF 解析）、`numpy`（数组运算）、`Pillow`（图像读写/拼图） |
| 输入 | 一个 `.glb` 文件（自备，注意素材版权） |
| 中文标注 | 系统需有中文字体（脚本会尝试常见路径，找不到需手动指定） |

```bash
pip install pygltflib numpy Pillow
```

## 🚀 快速开始

```bash
git clone https://github.com/ggq-eng/glb-texture-extract.git
cd glb-texture-extract

# 1) 摸清结构：场景图 / 网格 / 材质 / 纹理
python analyze.py 你的模型.glb

# 2) 导出原始贴图 + 零光照对照渲染
python export_original.py 你的模型.glb

# 3) ORM 三通道拆解
python explain_atlas.py 你的模型.glb

# 4) 拼带中文标注的贴图总览图
python make_tex_sheet.py
```

## 📂 目录结构

```text
  - .gitignore
  - LICENSE
  - README.md
  - analyze.py              场景图遍历：节点 / 网格 / 材质 / 纹理引用链
  - analyze2.py             二轮分析：多视角渲染与缓存
  - build_cache.py          构建网格缓存（npz），避免重复解析大模型
  - explain_atlas.py        ORM 三通道拆解与说明
  - explore.py              交互式探索 GLB 内部结构
  - export_original.py      导出内嵌原始贴图 + 零光照纯原色对照图
  - make_tex_sheet.py       生成带中文标注的贴图总览图
```

## 🧭 各脚本详解

| 脚本 | 作用 | 产出 |
|---|---|---|
| `analyze.py` | 首次解析：`walk(node_idx, depth, g)` 递归遍历场景图，打印节点层级、mesh 引用、材质与纹理对应关系 | 结构报告 |
| `explore.py` | 交互式探索：逐个节点查看属性，适合边看边定位 | 控制台 |
| `analyze2.py` | 二轮分析：基于缓存做多视角渲染（正面 / 侧面 / 背面 / 底部） | 多视角 PNG |
| `build_cache.py` | 把网格数据存成 `.npz` 缓存，大模型二次分析时不用重新解析 | `mesh_cache.npz` |
| `export_original.py` | `save(tex, name)` 导出 GLB 内嵌的**原始贴图字节**，并渲一版「零光照纯原色」对照图 | 原图 PNG + 对照 PNG |
| `explain_atlas.py` | 拆解 ORM 贴图：R/G/B 三通道分别可视化，说明每个通道控制什么 | 通道拆解 PNG |
| `make_tex_sheet.py` | `cjk_font(size)` 加载中文字体，把所有贴图与通道拼成一张带标注的总览图 | 总览 PNG |

## 📤 输出说明

| 产物 | 说明 |
|---|---|
| 原始贴图 PNG | GLB 内嵌贴图按原分辨率导出（不重采样） |
| 零光照纯原色对照图 | 不打光，只看贴图本身——用于区分「贴图暗」还是「光照暗」 |
| 多视角预览 PNG | 正面 / 侧面 / 背面 / 底部 |
| ORM 通道拆解 PNG | AO / Roughness / Metallic 三张单独的灰度图 |
| 贴图总览 PNG | 带中文标注的一张汇总图，可直接贴进交付文档 |
| `mesh_cache.npz` | 网格数据缓存，加速二次分析 |

## 🔬 工作原理

```text
.glb ──pygltflib──▶ glTF 结构树
                      │
        analyze.walk()├──▶ 节点层级 / mesh / 材质 / 纹理 引用链
                      │
        export_original├──▶ 按 bufferView 取出原始贴图字节 → PNG
                      │
        explain_atlas ├──▶ 金属粗糙度贴图拆 R/G/B 三通道
                      │
        make_tex_sheet└──▶ Pillow 拼图 + CJK 文字标注
```

- **glTF 的贴图不存成独立文件**，而是放在 `buffer`（二进制块）里，由 `bufferView`
  描述偏移与长度。所谓「导出贴图」就是按 `bufferView` 把这段字节切出来还原成 PNG。
- **`metallicRoughness` 是打包贴图**：三个不同的物理量挤在一张图的 R/G/B 三个通道里，
  拆开看才能确认每个通道是否正确（很多「模型发黑」就是 AO 通道接到了 Metallic 上）。

## ⚙️ 配置说明

| 项 | 说明 |
|---|---|
| 模型路径 | 各脚本底部的调用处传入 |
| 中文字体 | `make_tex_sheet.py` 的 `cjk_font()` 内置常见字体路径，找不到时需手动指定 |
| 视角参数 | `analyze2.py` 里的相机方位角/仰角 |

> ⚠️ 脚本头部常量含作者本机路径（已统一成 `C:\Users\<你的用户名>\...` 占位），
> 使用前请改成你自己的模型所在目录。

## ❓ 常见问题

**Q：`.gltf`（文本格式）能用吗？**
核心逻辑一致，但贴图通常以外部文件形式引用而非内嵌 buffer，
`export_original.py` 需要按 `image.uri` 读文件而不是切 buffer。

**Q：模型很大，解析很慢怎么办？**
先跑 `build_cache.py` 生成 `.npz` 缓存，之后 `analyze2.py` 会直接读缓存。

**Q：导出的贴图是黑的？**
先看 `export_original.py` 的「零光照纯原色」对照图——如果原图也是黑的，
说明贴图本身如此（或 Alpha 通道问题）；如果原图正常，是光照/材质参数问题。

**Q：ORM 三个通道分别是什么？**
glTF 规范约定打包在 `metallicRoughness` 贴图里：
**R = Ambient Occlusion（环境光遮蔽）、G = Roughness（粗糙度）、B = Metallic（金属度）**。

## ⚠️ 注意事项

- **素材版权自负**：从素材站下载的模型与贴图，其授权范围各不相同，
  本仓库只提供工具，不含任何模型与贴图
- 脚本是为一次性排查任务写的，硬编码路径较多，使用前先改
- 部分脚本输出的 PNG 体积可能很大（原图分辨率导出），注意磁盘空间

## 📄 许可

MIT License · 详见 [LICENSE](LICENSE)
