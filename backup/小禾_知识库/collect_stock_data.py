#!/usr/bin/env python3
"""
个股深度报告数据采集脚本
用法: python3 collect_stock_data.py <股票代码>
示例: python3 collect_stock_data.py 000001.SZ
输出: ~/.hermes/knowledge_base/data/{code}_data.json
"""
import json, os, sys, time, warnings
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import akshare as ak

warnings.filterwarnings("ignore")
TIMEOUT = 15
OUTPUT_DIR = os.path.expanduser("~/.hermes/knowledge_base/data")

# Tushare 连接单例：避免 3 个线程各建一个 HTTP 连接
_PRO_API = None
_TUSHARE_TOKEN = None


def _get_tushare_token():
    global _TUSHARE_TOKEN
    if _TUSHARE_TOKEN is not None:
        return _TUSHARE_TOKEN
    try:
        cfg = json.load(open(os.path.expanduser("~/.mcp.json")))
        for s in cfg.get("mcpServers", {}).values():
            url = s.get("url", "")
            if "tushare" in url:
                _TUSHARE_TOKEN = url.split("token=")[-1].split("&")[0]
                return _TUSHARE_TOKEN
    except Exception:
        pass
    _TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
    return _TUSHARE_TOKEN


def _init_tushare():
    global _PRO_API
    if _PRO_API is not None:
        return _PRO_API
    import tushare as ts
    ts.set_token(_get_tushare_token())
    _PRO_API = ts.pro_api()
    return _PRO_API

def fmt_code(code: str) -> str:
    code = code.strip().upper()
    if "." in code:
        return code
    if code.startswith(("0", "3")):
        return f"{code}.SZ"
    if code.startswith(("6", "9")):
        return f"{code}.SH"
    if code.startswith("4") or code.startswith("8"):
        return f"{code}.BJ"
    return code

def short_code(ts_code: str) -> str:
    return ts_code.split(".")[0]

def get_basic_info(ts_code: str) -> dict:
    try:
        pro = _init_tushare()
        df = pro.stock_basic(ts_code=ts_code,
            fields="ts_code,name,industry,area,list_date,market")
        if df is None or df.empty:
            return {"source": "tushare", "error": "not found"}
        r = df.iloc[0].to_dict()
        try:
            df2 = pro.stock_company(ts_code=ts_code,
                fields="chairman,manager,reg_capital,setup_date,province,city,website,main_business")
            if df2 is not None and not df2.empty:
                r.update(df2.iloc[0].to_dict())
        except Exception:
            pass
        return {"source": "tushare", "data": r}
    except Exception as e:
        return {"source": "tushare", "error": str(e)}

def get_realtime_quote(ts_code: str) -> dict:
    # 腾讯证券行情接口字段索引: http://qt.gtimg.cn
    QT = {"name":1, "price":3, "pre_close":4, "open":5, "volume":6,
          "high":33, "low":34, "change_pct":32, "pe":39, "market_cap":45, "turnover":38}
    try:
        import requests as req
        sc = short_code(ts_code)
        if ts_code.endswith(".SZ"):
            q_code = f"sz{sc}"
        elif ts_code.endswith(".SH"):
            q_code = f"sh{sc}"
        else:
            q_code = f"bj{sc}"
        r = req.get(f"http://qt.gtimg.cn/q={q_code}", timeout=TIMEOUT)
        r.encoding = "gbk"
        raw = r.text
        if "~" not in raw:
            return {"source": "qt.gtimg.cn", "error": "no data"}
        parts = raw.strip().split("~")
        return {"source": "qt.gtimg.cn", "data": {
            "name": parts[QT["name"]], "price": float(parts[QT["price"]]),
            "pre_close": float(parts[QT["pre_close"]]), "open": float(parts[QT["open"]]),
            "volume": int(parts[QT["volume"]]), "high": float(parts[QT["high"]]),
            "low": float(parts[QT["low"]]), "change_pct": float(parts[QT["change_pct"]]),
            "pe": float(parts[QT["pe"]]) if parts[QT["pe"]] else 0,
            "market_cap": float(parts[QT["market_cap"]]) if parts[QT["market_cap"]] else 0,
            "turnover": float(parts[QT["turnover"]]) if parts[QT["turnover"]] else 0,
        }}
    except Exception as e:
        return {"source": "qt.gtimg.cn", "error": str(e)}

def get_financial_data(ts_code: str) -> dict:
    try:
        pro = _init_tushare()
        now = datetime.now()
        periods = [f"{y}1231" for y in range(now.year - 1, now.year - 6, -1)]
        results = []
        for p in periods:
            try:
                df = pro.fina_indicator(ts_code=ts_code, period=p,
                    fields="end_date,eps,roe,roa,grossprofit_margin,netprofit_margin,"
                           "total_revenue,operate_profit,n_income,bps,"
                           "debt_to_assets,current_ratio")
                if df is not None and not df.empty:
                    r = df.iloc[0].to_dict()
                    r["period"] = p
                    results.append(r)
            except Exception:
                pass
        return {"source": "tushare", "data": results}
    except Exception as e:
        return {"source": "tushare", "error": str(e)}

def get_research_reports(ts_code: str) -> dict:
    try:
        sc = short_code(ts_code)
        df = ak.stock_research_report_em(symbol=sc)
        if df is None or df.empty:
            return {"source": "akshare", "data": []}
        df = df.tail(30)
        reports = []
        for d in df.to_dict("records"):
            reports.append({
                "date": str(d.get("date", "")),
                "org": str(d.get("org_name", "")),
                "title": str(d.get("title", "")),
                "rating": str(d.get("rating", "")),
            })
        return {"source": "akshare", "data": reports}
    except Exception as e:
        return {"source": "akshare", "error": str(e)}

def get_daily_kline(ts_code: str) -> dict:
    try:
        pro = _init_tushare()
        end = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
        df = pro.daily(ts_code=ts_code, start_date=start, end_date=end)
        if df is None or df.empty:
            return {"source": "tushare", "data": []}
        return {"source": "tushare", "data": df.tail(30).to_dict("records")}
    except Exception as e:
        return {"source": "tushare", "error": str(e)}

def collect_all(code: str) -> dict:
    ts_code = fmt_code(code)
    result = {
        "stock_code": ts_code,
        "collect_time": datetime.now().isoformat(),
        "data": {},
    }
    tasks = {
        "basic_info": get_basic_info,
        "realtime_quote": get_realtime_quote,
        "financial_data": get_financial_data,
        "research_reports": get_research_reports,
        "daily_kline": get_daily_kline,
    }
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {k: ex.submit(fn, ts_code) for k, fn in tasks.items()}
        for k, fut in futures.items():
            try:
                result["data"][k] = fut.result(timeout=TIMEOUT)
            except TimeoutError:
                result["data"][k] = {"error": "timeout"}
            except Exception as e:
                result["data"][k] = {"error": str(e)}
    return result

def main():
    if len(sys.argv) < 2:
        print("用法: python3 collect_stock_data.py <股票代码>")
        print("示例: python3 collect_stock_data.py 000001.SZ")
        sys.exit(1)
    code = sys.argv[1]
    print(f"采集 {fmt_code(code)} 数据...")
    result = collect_all(code)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = f"{fmt_code(code).replace('.','_')}_data.json"
    out_file = os.path.join(OUTPUT_DIR, fname)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    for key, val in result["data"].items():
        status = "OK" if "error" not in val else "FAIL"
        src = val.get("source", "?")
        print(f"  [{status}] {key} ({src})")
    print(f"输出: {out_file}")

if __name__ == "__main__":
    main()
