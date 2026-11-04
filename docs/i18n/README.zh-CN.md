# Portfolio Models — 量化投资组合优化与风险管理

[English](../../README.md) · **简体中文** · [Русский](README.ru-RU.md)

Portfolio Models 是面向智能代理的开源量化金融技能，提供**投资组合优化、资产配置和风险管理**的数学定义、可运行的 Python 参考实现、可核验的学术文献，以及严格的历史回测规范。采用**渐进式信息披露**：代理先读取简短的 `SKILL.md`，仅在任务需要时加载具体模型、代码或文献。

## 安装

```bash
npx skills add KaigorodovTuskul/portfolio-models-agent-skill --skill portfolio-models
```

也可以将 `skills/portfolio-models/` 复制到支持 Agent Skills 的客户端技能目录。入口文件为 [`SKILL.md`](../../skills/portfolio-models/SKILL.md)，项目的**代码、技术文档和代理指令统一使用英文**。

## 已实现的模型

涵盖均值—方差优化（Markowitz MVO）、全球最小方差（GMV）、Ledoit–Wolf / OAS 协方差收缩、最大夏普比率、Black–Litterman、等风险贡献（ERC）、一般风险预算、层次风险平价（HRP，单链接/平均链接）、最大分散化、均值—半方差、CVaR / Mean-CVaR、CDaR / Mean-CDaR、鲁棒均值与协方差优化、1-Wasserstein DRO-CVaR、Kelly 增长优化、熵风险、最小跟踪误差以及带换手惩罚的最小方差。

**重要边界：**本项目中 CDaR 的优化对象是按固定权重计算的**加法累计损益路径**，不能与复利净值回撤混淆。Wasserstein DRO-CVaR 是明确假设下的特殊形式，不是通用分布鲁棒优化引擎。数学目标函数之间的数值不能直接互相排名。

## 运行与检验

需要 Python 3.10 或更高版本。

```bash
python -m pip install -r requirements.txt
python skills/portfolio-models/scripts/comparison_demo.py
python -m pytest -q tests
python scripts/stress_solvers.py
python scripts/goal_workflow.py check
```

可以运行 `portfolio_cli.py` 从按时间排序的 CSV（日期列 + 以小数表示的同期资产总回报）拟合模型。例如：

```bash
python skills/portfolio-models/scripts/portfolio_cli.py datasets/synthetic_monthly_returns.csv --model mean-cvar --alpha 0.90 --lambda-risk 3
```

随附数据是**确定性生成的合成数据**，不代表历史市场收益，也不用于证明策略超额收益。项目没有 GitHub Actions 测试流程，所有验证在本地执行。

## 文献与质量标准

原始研究来源包含英文、俄文和中文论文，并在[文献目录](../../skills/portfolio-models/references/source-catalog.md)中明确标注获取方式与方法适用范围。金融实证结论必须使用事前可获得数据、统一的样本外日期、可执行的资产、交易成本、可比风险水平以及简单基准。

仓库提供四个独立评审维度的流程与可核验的质量门槛；未完成的外部评审不能以内部评分代替。详见[评审流程](../../workflows/goal-workflow.md)。

## 许可

MIT License，详见[许可证](../../LICENSE)。项目用于研究和教育，不提供投资建议、真实交易执行或历史盈利保证。
