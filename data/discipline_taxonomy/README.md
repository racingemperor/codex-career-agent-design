# 学科域分类框架

这个目录用于预留非工科专业扩展，不替代当前 `data/major_taxonomy/` 中已经落地的工科就业大类数据库。

Pipeline 的专业分类应分两步：

1. 先识别用户专业所属的 `discipline_domain`。
2. 再进入对应学科域的就业分类逻辑。

当前只有 `engineering` 具备完整静态数据库。`science`、`humanities`、`social_science`、`business`、`arts_design`、`medicine_health`、`agriculture`、`law_public_affairs` 和 `interdisciplinary` 先保留域定义、采集计划和输出接口，后续再补具体专业目录、就业大类、岗位族和证据规则。

## 学科域逻辑差异

- 工科：看工程项目、工具链、实验/仿真/制造/部署、可验证交付。
- 理科：看数学建模、实验方法、科研训练、数据分析、可迁移工程化能力。
- 文科：看研究、写作、语言、内容判断、文本分析、文化/历史/政策理解。
- 社科：看调研、统计、政策分析、组织理解、用户研究、咨询与公共事务。
- 商科：看财务、运营、市场、战略、投研、数据分析和商业结果。
- 艺术设计：看作品集、审美判断、设计过程、表达媒介、用户/品牌理解。
- 医学健康：看专业资质、实验/临床/法规、医疗器械、生物医药和健康数据。
- 农学：看实验田/养殖/食品/生态/资源、生产流程和产业链理解。
- 法学与公共事务：看法律检索、案例分析、合规、政策、文书和表达。
- 跨专业：不作为单一学科，而作为桥接层，描述从原专业到目标岗位需要补齐的课程、项目、作品、证书或实习证据。

## 运行规则

当用户专业命中已落地的学科域数据库时，分类器应输出具体 `primary_cluster`、`cross_tags`、`peer_majors` 和 `skill_gaps_by_target`。

当用户专业属于尚未落地的学科域时，分类器不要硬套工科分类。应输出：

- `discipline_domain`
- `taxonomy_status = "pending_static_database"`
- `available_reasoning_basis`
- `recommended_data_to_collect`
- `provisional_role_families`
- `needs_user_confirmation`

这样可以继续给出谨慎的方向建议，同时明确静态数据库还未覆盖。

