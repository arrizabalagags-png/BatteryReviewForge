# VoltPeer 可复现绘图包

首批三个原型沿用网站resource_id：`full_cell`、`li_li`、`operando_xrd`。对应全电池循环/可选实测CE及关联电压、Li/Na signed对称轨迹、坐标键XRD热图/可选同步电压。每个文件夹提供完整独立源码和配置，不依赖完整仓库或全局安装Skill。用户复制整个包到自己的研究项目，优先配置，再适配CSV，最后才改项目副本源码。

运行接口：

```text
python src/plot.py --config config.demo.json --out Working-demo
python checks.py --working Working-demo
```

真实输入从config.real.example.json复制并填全确认信息；演示生成器只能显式运行，不能作为真实渲染后备。未知单位、分母/面积、关键工况、重复/缺失XRD网格或不同步区间停止；不替用户猜。原CSV保持，结果版本化。字长/新分组/新范围自动布局并检查图例，超范围显式请求调整。

输入契约逐包声明实际支持的单位及条件，不把全电池N/P、E/C要求套给对称电池或XRD。颜色按真实样品/物理量/剖面圈数分配，同一轨迹放大视图保留颜色。默认10种互异曲线色，不够时停止；可用足够的`style.colors`或完整`style.curve_colors`映射，重复/透明/过近或对白底对比不足的颜色先停，绝不循环复用。内部记录保存实际Line2D颜色身份；XRD色标对应强度，不把热图强度配色误认为样品色。

字体检查直接读取最终图中实际可见的标题、全部样品名、图例、轴/色标单位和刻度，逐段核对所选字体的真实 cmap，不取前50行样品作代表。可用的`style.font_family`优先保留；必要时使用完整覆盖该文字的本机字体并在内部`font_glyph_checks`记录字体家族、文件SHA及fallback。所有可用字体仍缺字时停止，不删改标签或交付缺字图。字体文件不随包分发；编辑或跨机器打开SVG文字时要核对当地字体，字形覆盖不代替最终视觉审查。

维护源在 `_runtime/` 和 `scripts/runtime_contract/`；打包器把共同实现复制到每包src并声明依赖，因此包内源码是可查看、可脱离仓库运行的真实实现，不是引用未提供父级build.py的入口。维护者应改源并重新准备包；使用者在项目副本改包，保留diff。

```text
python scripts/package_recipe_packs.py --out outputs/recipe-packs
python -m unittest discover -s tests -p test_recipe_packs.py -v
```

打包会生成3个ZIP和recipe-packs.json哈希/版本清单，已有输出目录会新建版本。网页登记这些包为现有资源的分发文件，不能再建重复Community身份。ZIP实际解压运行、技术盲集适配和应停测试与真实模型EVAL分开，参见evals/recipe_packs/PROTOCOL.md。科学与人工视觉审查仍独立进行，不宣传包能训练模型或使任何模型“自动变强”。
