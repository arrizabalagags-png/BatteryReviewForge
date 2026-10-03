# VoltPeer 0.12.0 源码同步 · 2026-10-03

本次同步科研绘图、Figure拼版、机理图、数据导入、论文写作、论证提纲与润色等16个Skill的源码、教学示例和分发包。版本保持Beta，完整原生宿主与当前模型行为门禁仍为NOT_RUN。

循环图的当前显示约定是容量、库伦效率与容量保持率用逐圈点；连续电压、光谱与EIS用实线；数据面板四周框线。全电池保持率需要明确参考圈/参考容量和匹配条件，Li‖Cu镀剥CE不强制配保持率；NMC811‖Li按半电池标注。这些是本项目选择的显示规则，不宣传为所有期刊的统一规定。

当前样例与配方为cycling-rule-v1.2.0，Skill/Starter为cycling-rule-v1.2.1。当前[Starter](../assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip)、[完整技能包](../downloads/v0.12.0-cycling-rule-v1.2.1/VoltPeer-v0.12.0.zip)和[35包索引](../downloads/v0.12.0-cycling-rule-v1.2.1/download-index.json)有固定大小与SHA；旧包保持原字节。

16个受影响示例、配方和Starter实际解压重画；190原CSV不改。35包/66独立Skill副本检查和当前完整包Python3.9独立52项检查通过；一圈、两圈、双轴CE和参考点留白另有真实执行证据。公开摘要见[循环交付记录](2026-10-03-cycling-delivery.json)。合成教学数据不证明材料性能；Zn-I2、flow等历史模型的缺失物理条件没有补造。

源码已上传并从GitHub API回读：`main`与`codex/public-skills`均指向`24970f5b0142bca80261a036a6d768143e251097`。提交树及12个关键文件的Git blob与大小匹配。[推送回执](2026-10-03-github-readback.json)。本记录更新作为后续日志提交，不改变固定分发ZIP；未创建Stable标签或新Release，未执行ECS部署。
