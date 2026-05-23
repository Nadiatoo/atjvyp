#!/usr/bin/env python3
"""
知识图谱清洗 + SQLite 建库
输入: _knowledge_graph.json (282题材, 1368公司)
输出: knowledge_base.db (companies / themes / associations + FTS5)

清洗策略:
  1. AKShare 获取 A 股真实股票名列表做白名单
  2. 有 6 位股票代码 → 可信
  3. 在白名单中 → 可信
  4. 以公司后缀结尾 + 2-8 字 → 保留
  5. 其余 → 清洗掉（VL 识别噪音）
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

INPUT = Path("/Users/tuqibiao/Downloads/2026复盘/知识星球数据库/_知识库/_knowledge_graph.json")
OUTPUT = Path("/Users/tuqibiao/.hermes/knowledge_base/knowledge_base.db")

# ── 公司后缀 ──────────────────────────────────────────────

COMPANY_SUFFIX = sorted([
    '股份', '科技', '集团', '电子', '智能', '控股', '实业', '国际',
    '技术', '电气', '新材', '光电', '微电', '半导体', '通信', '信息',
    '软件', '网络', '数据', '互联', '汽车', '医疗', '生物', '化学',
    '制药', '能源', '矿业', '钢铁', '机械', '装备', '制造', '重工',
    '动力', '银行', '证券', '保险', '地产', '建设', '交通', '航空',
    '航天', '船舶', '物流', '传媒', '文化', '教育', '环境', '环保',
    '食品', '农牧', '医药', '器械', '仪器', '仪表', '自动化',
    '机器人', '激光', '光学', '精密', '精工', '电机', '电缆',
    '安防', '玻璃', '陶瓷', '建材', '装饰', '纺织', '服装',
    '包装', '印刷', '家具', '家电', '照明', '供热', '水务',
    '燃气', '投资', '资本', '租赁', '担保', '信托', '期货',
    '基金', '酒店', '旅游', '传媒', '广告', '会展',
    '元器件', '电路', '封装', '晶圆', '硅片', '衬底',
    '磁性', '传感', '数控', '测控', '无损', '互联',
    '卫星', '导航', '无人机', '航天', '发动机',
    '材料', '化工', '合金', '碳素', '稀土', '磁材',
    '风电', '光伏', '核电', '储能', '氢能',
    '交通', '高速', '铁路', '港口', '机场', '航运',
    '园区', '城投', '开发',
    '养殖', '种业', '林业', '渔业', '饲料',
    '饮料', '酒业', '乳业', '调味', '油脂',
    '纸业', '炭业', '矿业', '盐化',
    '云计算', '大数据', '人工智能', '区块链',
    '在线', '数字', '智慧', '云端',
], key=lambda x: -len(x))  # 长后缀优先匹配

# ── 噪音模式 ──────────────────────────────────────────────

NOISE_WORDS = {
    '所有', '全部', '表格', '图片', '上为', '下图', '识别',
    '无法', '完整', '准确', '以上', '视频', '语音', '图像',
    '结合', '实时', '物体', '显示', '内容', '身份', '手势',
    '人脸', '专注', '中的', '穿着', '潜水', '装备',
    '白色', '字体', '文字', '数字', '提取', '所示',
}

# 表头/分类/描述性短语（不含公司名的描述文本）
DESCRIPTIVE_PATTERNS = [
    r'^(AI|CPU|GPU|FPGA|MCU|SoC|ASIC|DSP|NPU|TPU|DRAM|NAND|NOR)[芯片]?$',
    r'^(各种|各类|相关|主要|核心|其他|以上|以下|部分)',
    r'^(存储|计算|训练|推理|加速|边缘|云端|终端|消费|工业|汽车|通信|算力|电源)芯片$',
    r'芯片(制造|设计|封装|测试|集成|应用|开发|产业链|公司|企业)$',
    r'(环节|领域|体系|系统|平台|材料|设备|制造|技术|网络|方案|服务|业务)$',
    r'^(代表|主要|相关|部分|具体|对应)',
    r'^[\w]+(芯片|存储|计算|处理器|加速器|服务器|交换机|路由器)$',
    r'^(服务器|交换机|路由器|光模块|连接器|传感器|控制器)',
    r'^(存储|训练|推理|加速|边缘|云端|专用)',
    r'(产业|行业|产业链|供应链|生态|体系)',
    r'^(未上市|上市公司|非上市|独角兽|初创)',
    r'^(产品|技术|方案|服务|平台|系统)(广泛)?应用于',
    r'^(提供|涵盖|包括|覆盖|涉及|布局|推动|构建|支持|提升)',
    r'^(以|为|如|即|或|和|及|与)(芯片|产品|公司|技术)',
    r'(开发|设计|制造|生产|销售|服务|集成|应用)$',
    r'^(专注|致力于|专注于|专攻)',
    r'^一位.*',
    r'^(以下|上述|图片中|图中|下表)',
    r'^(任何|没有|无)(可|不可)',
    r'^(成立|合资|合作)',
    r'^(推动|促进|实现|完成|达成)',
    r'^(国内|国际|全球|中国)(领先|最大|首个|唯一)',
]


def load_real_stock_names():
    """使用 AKShare 获取真实 A 股股票名称列表"""
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        names = set(df['名称'].str.strip())
        print(f"AKShare: 获取 {len(names)} 只 A 股真实名称")
        return names
    except Exception as e:
        print(f"AKShare 不可用 ({e})，使用本地缓存")
        # 回退：从知识图谱中收集有股票代码的公司名
        return None


def has_stock_code(theme_dict: dict) -> bool:
    """检查公司是否在任何题材下有有效股票代码"""
    for v in theme_dict.values():
        v = v.strip() if isinstance(v, str) else ''
        if re.match(r'^\d{6}(\.(SZ|SH|sz|sh))?$', v):
            return True
    return False


def looks_like_company(name: str) -> bool:
    """判断名称是否像真实公司名"""
    if not (2 <= len(name) <= 8):
        return False
    if not re.search(r'[一-鿿]', name):
        return False
    for suffix in COMPANY_SUFFIX:
        if name.endswith(suffix) and len(name) > len(suffix):
            return True
    return False


def is_noise(name: str) -> tuple[bool, str]:
    """多维度噪音检测"""
    name = name.strip()

    if len(name) <= 1:
        return True, "过短"
    if len(name) > 15:
        return True, f"过长({len(name)}字)"
    if '<br>' in name.lower():
        return True, "含HTML"
    if not re.search(r'[一-鿿]', name):
        return True, "无中文"
    if name.endswith(('的', '了', '是', '为', '及', '或')):
        return True, f"末字'{name[-1]}'异常"

    for w in NOISE_WORDS:
        if w in name:
            return True, f"噪音词'{w}'"

    for pat in DESCRIPTIVE_PATTERNS:
        if re.match(pat, name):
            return True, f"描述性短语: {pat}"

    return False, ""


def split_html(name: str) -> list[str]:
    parts = re.split(r'<br\s*/?>', name, flags=re.IGNORECASE)
    return [p.strip() for p in parts if looks_like_company(p.strip()) or has_stock_code({})]


def clean(data: dict, real_names: set | None) -> dict:
    companies = data.get('company_themes', {})
    themes = data.get('theme_companies', {})

    kept = {}
    removed = []
    split_added = []
    stats = {'by_code': 0, 'by_whitelist': 0, 'by_suffix': 0, 'removed': 0}

    for name, theme_dict in companies.items():
        name = name.strip()
        is_noise_flag, reason = is_noise(name)

        if is_noise_flag:
            if 'br' in name.lower():
                parts = split_html(name)
                if parts:
                    for part in parts:
                        if part not in kept:
                            kept[part] = {}
                        for t, v in theme_dict.items():
                            if t and t.strip():
                                kept[part][t.strip()] = v.strip() if isinstance(v, str) and v.strip() else ''
                    split_added.extend(parts)
                    removed.append(f"拆分 [{name}] → {parts}")
                    continue
            removed.append(f"噪音 [{name}] ({reason})")
            stats['removed'] += 1
            continue

        # 分级可信度判断
        has_code = has_stock_code(theme_dict)
        in_whitelist = real_names and name in real_names
        looks_company = looks_like_company(name)
        # 有实质数据（非空值）即使无代码也可能是真公司（如宁德时代只有产品描述无代码）
        has_data = any(v.strip() for v in theme_dict.values() if isinstance(v, str) and v.strip())

        if has_code:
            stats['by_code'] += 1
        elif in_whitelist:
            stats['by_whitelist'] += 1
        elif looks_company:
            stats['by_suffix'] += 1
        elif has_data and 2 <= len(name) <= 8 and re.search(r'[一-鿿]', name):
            stats['by_suffix'] += 1  # 有数据的中文短名称也保留
        else:
            removed.append(f"不可信 [{name}] (无代码/无后缀/无数据)")
            stats['removed'] += 1
            continue

        clean_themes = {}
        for t, v in theme_dict.items():
            t = t.strip()
            if not t:
                continue
            v = v.strip() if isinstance(v, str) else ''
            clean_themes[t] = v

        if name not in kept:
            kept[name] = {}
        kept[name].update(clean_themes)

    # 清理 theme_companies
    cleaned_themes = {}
    for theme, comps in themes.items():
        theme = theme.strip()
        if not theme:
            continue
        valid_comps = [c for c in comps if c in kept]
        cleaned_themes[theme] = valid_comps

    print(f"\n清洗统计:")
    print(f"  有股票代码 → 保留: {stats['by_code']}")
    print(f"  在白名单中 → 保留: {stats['by_whitelist']}")
    print(f"  后缀匹配   → 保留: {stats['by_suffix']}")
    print(f"  移除噪音: {stats['removed']}")
    print(f"  HTML拆分新增: {len(split_added)}")

    return {
        'company_themes': kept,
        'theme_companies': cleaned_themes,
        '_cleaned': {'removed': removed, 'split_added': split_added, 'stats': stats}
    }


# ── SQLite 建库 ───────────────────────────────────────────

def build_db(data: dict, db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executescript("""
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL REFERENCES companies(id),
            theme_id INTEGER NOT NULL REFERENCES themes(id),
            stock_code TEXT DEFAULT '',
            description TEXT DEFAULT '',
            UNIQUE(company_id, theme_id)
        );

        CREATE INDEX idx_assoc_company ON associations(company_id);
        CREATE INDEX idx_assoc_theme ON associations(theme_id);
        CREATE INDEX idx_assoc_code ON associations(stock_code) WHERE stock_code != '';
    """)

    companies = data['company_themes']
    themes_data = data['theme_companies']

    theme_ids = {}
    for theme_name in sorted(themes_data.keys()):
        conn.execute("INSERT INTO themes (name) VALUES (?)", (theme_name,))
        theme_ids[theme_name] = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    company_count = 0
    assoc_count = 0
    empty_count = 0

    for company_name in sorted(companies.keys()):
        conn.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
        company_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        company_count += 1

        for theme_name, value in companies[company_name].items():
            if theme_name not in theme_ids:
                conn.execute("INSERT INTO themes (name) VALUES (?)", (theme_name,))
                theme_ids[theme_name] = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            stock_code = ''
            description = value
            if value:
                if re.match(r'^\d{6}$', value):
                    stock_code = value
                    description = ''
                elif re.match(r'^\d{6}\.(SZ|SH|sz|sh)$', value):
                    stock_code = value.upper()
                    description = ''

            conn.execute(
                "INSERT OR IGNORE INTO associations (company_id, theme_id, stock_code, description) VALUES (?, ?, ?, ?)",
                (company_id, theme_ids[theme_name], stock_code, description)
            )
            assoc_count += 1
            if not value:
                empty_count += 1

    # 中文不适合 FTS5 默认分词器，用 LIKE + 索引即可
    # 数据量小(1000+公司, 280+题材)，LIKE 效率足够

    conn.commit()

    print(f"\n数据库: {db_path}")
    print(f"  公司: {company_count} 家")
    print(f"  题材: {len(theme_ids)} 个")
    print(f"  关联: {assoc_count} 条 (空值 {empty_count})")

    conn.close()
    return db_path


def main():
    print(f"读取: {INPUT}")
    with open(INPUT) as f:
        raw = json.load(f)

    print(f"原始: {len(raw['theme_companies'])} 题材, {len(raw['company_themes'])} 公司")
    print("获取 A 股真实名单...")

    real_names = load_real_stock_names()

    cleaned = clean(raw, real_names)
    build_db(cleaned, OUTPUT)

    backup = INPUT.parent / "_knowledge_graph_cleaned.json"
    with open(backup, 'w') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print(f"备份: {backup}")


if __name__ == "__main__":
    main()
