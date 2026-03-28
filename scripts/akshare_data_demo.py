#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "akshare",
#     "pandas",
# ]
# ///
# -*- coding: utf-8 -*-
"""
akshare 数据获取示例脚本

当 tushare 不可用时，使用 akshare 作为替代数据源。
akshare 是纯 Python 开源库，无需 API Token，直接安装使用。

数据覆盖：
- 日线/分钟线行情（东方财富接口）
- 股票列表（全市场）
- 北向资金（沪深港通）
- 融资融券（沪/深分开）
- 个股主力资金流
- 财务指标/财务摘要
- 大盘指数
- 板块资金流
- 新闻公告

注意：akshare 数据主要来源于东方财富、新浪等财经网站，
部分接口有频率限制，请勿高频调用。
"""

import os
import akshare as ak
import pandas as pd

# ---------- 环境说明 ----------
# akshare 无需 API Token，无需设置环境变量
# 如需设置代理，可通过环境变量 HTTPS_PROXY / HTTP_PROXY


def is_tushare_available():
    """检查 tushare 是否可用"""
    try:
        import tushare as ts
        token = os.getenv("TUSHARE_TOKEN")
        api_url = os.getenv("TUSHARE_URL")
        if not token or not api_url:
            return False
        pro = ts.pro_api(token)
        pro._DataApi__http_url = api_url
        pro.stock_basic(exchange='', list_status='L', fields='ts_code', limit=1)
        return True
    except Exception:
        return False


def get_stock_list():
    """
    获取 A股股票列表
    返回：DataFrame，字段包括 序号/代码/名称/最新价/涨跌幅/成交量/成交额/流通市值等
    """
    try:
        data = ak.stock_zh_a_spot_em()
        print(f"股票列表获取成功：{len(data)} 只股票")
        print(data.head(5)[['序号', '代码', '名称', '最新价', '涨跌幅']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取股票列表失败：{e}")
        return None


def get_daily_data(ts_code, start_date, end_date, adjust="qfq"):
    """
    获取个股日线数据（东方财富）
    参数：
        ts_code: 股票代码，如 '000564' 或 '600519'
        start_date: 开始日期，格式 YYYYMMDD
        end_date: 结束日期，格式 YYYYMMDD
        adjust: 复权类型，'qfq'=前复权，'hfq'=后复权，''=不复权
    返回：DataFrame，字段包括 日期/股票代码/开盘/收盘/最高/最低/成交量/成交额/涨跌幅/换手率等
    """
    try:
        # akshare 使用不带后缀的代码
        symbol = ts_code.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
        data = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        print(f"{ts_code} 日线数据获取成功：{len(data)} 条")
        print(data.head(5)[['日期', '开盘', '收盘', '最高', '最低', '涨跌幅']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取日线数据失败：{e}")
        return None


def get_minute_data(ts_code, start_date, end_date, adjust="qfq"):
    """
    获取分钟线数据（东方财富）
    参数：
        ts_code: 股票代码，如 '000564'
        start_date: 开始日期，格式 YYYYMMDD
        end_date: 结束日期，格式 YYYYMMDD
        adjust: 复权类型
    返回：DataFrame
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        data = ak.stock_zh_a_hist(
            symbol=symbol,
            period="60",  # 60分钟线，可选 1/5/15/30/60
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        print(f"{ts_code} 分钟数据获取成功：{len(data)} 条")
        return data
    except Exception as e:
        print(f"获取分钟数据失败：{e}")
        return None


def get_realtime_data(ts_code):
    """
    获取实时行情（东方财富实时）
    参数：ts_code 如 '000564'
    返回：DataFrame
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        data = ak.stock_zh_a_spot_em()
        result = data[data['代码'] == symbol]
        print(f"{ts_code} 实时行情：")
        print(result[['代码', '名称', '最新价', '涨跌幅', '成交量', '成交额']].to_string(index=False))
        return result
    except Exception as e:
        print(f"获取实时行情失败：{e}")
        return None


def get_financial_indicator(ts_code, start_year="2020"):
    """
    获取财务指标数据（东方财富）
    参数：
        ts_code: 股票代码，如 '000564'
        start_year: 起始年份，如 '2020'
    返回：DataFrame，字段包括 ROE/毛利率/净利率/资产负债率/每股收益/每股净资产等
          非常详细，覆盖主要财务指标几十项
    注意：akshare 返回的列名与 tushare 不同，需根据实际列名读取
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        data = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=start_year)
        print(f"{ts_code} 财务指标获取成功：{len(data)} 期")
        # 打印前几行列名，确认可用列
        print(f"可用列名：{list(data.columns[:10])}")
        print(data.head(3).to_string())
        return data
    except Exception as e:
        print(f"获取财务指标失败：{e}")
        return None


def get_financial_abstract(ts_code):
    """
    获取财务摘要数据（东方财富）
    返回：DataFrame，以 '选项'/'指标' 为索引，多期数据为列
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        data = ak.stock_financial_abstract(symbol=symbol)
        print(f"{ts_code} 财务摘要获取成功")
        # 取最近一期数据
        latest = data[['选项', '指标', data.columns[-1]]].tail(10)
        print(latest.to_string(index=False))
        return data
    except Exception as e:
        print(f"获取财务摘要失败：{e}")
        return None


def get_income(ts_code, start_year=None):
    """
    获取利润表（东方财富）
    返回：DataFrame，含净利润、营业总收入等
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        # 判断市场，akshare 财务接口需要 SH/SZ 前缀
        if symbol.startswith('6'):
            symbol = "SH" + symbol
        else:
            symbol = "SZ" + symbol
        data = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        print(f"{ts_code} 利润表获取成功：{len(data)} 期")
        print(data.tail(3).to_string())
        return data
    except Exception as e:
        print(f"获取利润表失败：{e}")
        return None


def get_balance_sheet(ts_code):
    """
    获取资产负债表（东方财富）
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        if symbol.startswith('6'):
            symbol = "SH" + symbol
        else:
            symbol = "SZ" + symbol
        data = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        print(f"{ts_code} 资产负债表获取成功：{len(data)} 期")
        return data
    except Exception as e:
        print(f"获取资产负债表失败：{e}")
        return None


def get_cash_flow(ts_code):
    """
    获取现金流量表（东方财富）
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        if symbol.startswith('6'):
            symbol = "SH" + symbol
        else:
            symbol = "SZ" + symbol
        data = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        print(f"{ts_code} 现金流量表获取成功：{len(data)} 期")
        return data
    except Exception as e:
        print(f"获取现金流量表失败：{e}")
        return None


def get_money_flow_individual(ts_code, market="sz"):
    """
    获取个股资金流（东方财富）
    参数：
        ts_code: 股票代码，如 '000564'
        market: 市场，'sh'=上海，'sz'=深圳
    返回：DataFrame，含主力/超大单/大单/中单/小单净流入和净占比
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        # 判断市场
        if symbol.startswith('6'):
            market = "sh"
        else:
            market = "sz"
        data = ak.stock_individual_fund_flow(stock=symbol, market=market)
        print(f"{ts_code} 个股资金流获取成功：{len(data)} 条")
        print(data.tail(5)[['日期', '收盘价', '涨跌幅', '主力净流入-净额', '主力净流入-净占比']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取个股资金流失败：{e}")
        return None


def get_money_flow_sector():
    """
    获取板块资金流（东方财富）
    返回：DataFrame，含行业/概念板块的主力资金净流入
    """
    try:
        data = ak.stock_sector_fund_flow_summary()
        print(f"板块资金流获取成功：{len(data)} 个板块")
        print(data.head(10).to_string())
        return data
    except Exception as e:
        print(f"获取板块资金流失败：{e}")
        return None


def get_hsgt_flow():
    """
    获取沪深港通资金流向（东方财富）
    返回：DataFrame，含沪股通/深股通/港股通的北向/南向资金
    """
    try:
        data = ak.stock_hsgt_fund_flow_summary_em()
        print("沪深港通资金流向获取成功：")
        print(data.to_string())
        return data
    except Exception as e:
        print(f"获取沪深港通资金流失败：{e}")
        return None


def get_hsgt_top10(trade_date=None):
    """
    获取沪深港通资金个股排行（东方财富）
    参数：trade_date 格式 YYYYMMDD，不传则默认最新
    返回：DataFrame
    """
    try:
        if trade_date:
            data = ak.stock_hsgt_hold_stock_em(start_date=trade_date, end_date=trade_date)
        else:
            data = ak.stock_hsgt_hold_stock_em()
        print(f"沪深港通个股排行获取成功：{len(data)} 条")
        print(data.head(10).to_string())
        return data
    except Exception as e:
        print(f"获取沪深港通个股排行失败：{e}")
        return None


def get_margin_sz(start_date=None, end_date=None):
    """
    获取融资融券-深市（东方财富，无参数版）
    注意：akshare 深市融资融券接口暂不支持日期范围筛选，返回全部历史数据
    返回：DataFrame，含融资余额/融券余额等
    """
    try:
        data = ak.macro_china_market_margin_sz()
        print(f"融资融券（深市）获取成功：{len(data)} 条")
        print(data.head(5).to_string())
        return data
    except Exception as e:
        print(f"获取融资融券（深市）失败：{e}")
        return None


def get_margin_sh(start_date=None, end_date=None):
    """
    获取融资融券-沪市（东方财富，无参数版）
    注意：akshare 沪市融资融券接口暂不支持日期范围筛选，返回全部历史数据
    """
    try:
        data = ak.macro_china_market_margin_sh()
        print(f"融资融券（沪市）获取成功：{len(data)} 条")
        print(data.head(5).to_string())
        return data
    except Exception as e:
        print(f"获取融资融券（沪市）失败：{e}")
        return None


def get_index_daily(index_code="000001", start_date="20260301", end_date="20260328"):
    """
    获取指数日线数据（东方财富）
    参数：
        index_code: 指数代码，'000001'=上证指数，'399001'=深证成指，'399006'=创业板指
    """
    try:
        data = ak.stock_zh_a_hist(
            symbol=index_code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=""
        )
        print(f"指数 {index_code} 日线获取成功：{len(data)} 条")
        print(data.head(5)[['日期', '开盘', '收盘', '最高', '最低', '涨跌幅']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取指数日线失败：{e}")
        return None


def get_board_industry():
    """
    获取申万行业板块列表
    返回：DataFrame
    """
    try:
        data = ak.stock_board_industry_name_em()
        print(f"申万行业板块获取成功：{len(data)} 个")
        print(data.head(10).to_string())
        return data
    except Exception as e:
        print(f"获取行业板块失败：{e}")
        return None


def get_board_concept():
    """
    获取概念板块列表（东方财富）
    返回：DataFrame
    """
    try:
        data = ak.stock_board_concept_name_em()
        print(f"概念板块获取成功：{len(data)} 个")
        print(data.head(10).to_string())
        return data
    except Exception as e:
        print(f"获取概念板块失败：{e}")
        return None


def get_news():
    """
    获取财经新闻（东方财富央视新闻）
    返回：DataFrame
    """
    try:
        data = ak.news_cctv()
        print("央视财经新闻获取成功：")
        print(data.head(5).to_string())
        return data
    except Exception as e:
        print(f"获取财经新闻失败：{e}")
        return None


def get_stock_news(ts_code):
    """
    获取个股新闻（东方财富）
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        data = ak.stock_news_em(symbol=symbol)
        print(f"{ts_code} 新闻获取成功：{len(data)} 条")
        print(data.head(5).to_string())
        return data
    except Exception as e:
        print(f"获取个股新闻失败：{e}")
        return None


def get_announcement(ts_code, date="20260301"):
    """
    获取个股公告（上交所/深交所）
    """
    try:
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        # 深交所公告
        try:
            data_szse = ak.stock_announcement_szse(symbol=symbol, start_date=date)
            if data_szse is not None and len(data_szse) > 0:
                print(f"{ts_code} 深交所公告获取成功：{len(data_szse)} 条")
                print(data_szse.head(3).to_string())
                return data_szse
        except:
            pass
        # 上交所公告
        try:
            data_sse = ak.stock_announcement_sse(symbol=symbol, start_date=date)
            if data_sse is not None and len(data_sse) > 0:
                print(f"{ts_code} 上交所公告获取成功：{len(data_sse)} 条")
                print(data_sse.head(3).to_string())
                return data_sse
        except:
            pass
        print(f"{ts_code} 公告获取失败（接口不可用）")
        return None
    except Exception as e:
        print(f"获取个股公告失败：{e}")
        return None


def get_futures_indicator(ts_code):
    """
    获取估值指标（东方财富）
    参数：ts_code 如 '000564'
    返回：PB、PE、PS 等
    """
    try:
        # 全市场 PB
        data = ak.stock_a_all_pb()
        symbol = ts_code.replace(".SH", "").replace(".SZ", "")
        result = data[data['代码'] == symbol]
        print(f"{ts_code} 估值数据：")
        print(result[['代码', '名称', '最新PB', 'PE(TTM)', '总市值']].to_string(index=False))
        return result
    except Exception as e:
        print(f"获取估值数据失败：{e}")
        return None


def main():
    """
    主函数
    """
    print("===== akshare 股票数据获取示例 =====")
    print()

    # 判断数据源
    if is_tushare_available():
        print("提示：tushare 可用，可使用 tushare 脚本获取数据")
        print("本脚本为 akshare 备用方案")
    else:
        print("提示：tushare 不可用，使用 akshare 获取数据")
    print()

    # ---------- 1. 获取股票列表 ----------
    print("【1】获取A股股票列表")
    stock_list = get_stock_list()
    print()

    # ---------- 2. 获取日线数据（最近30天） ----------
    import datetime
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d')
    print(f"【2】获取日线数据：{start_date} 至 {end_date}")
    # 使用平安银行测试
    get_daily_data('000001.SZ', start_date, end_date)
    print()

    # ---------- 3. 获取财务指标 ----------
    print("【3】获取财务指标（最近2年）")
    get_financial_indicator('000001.SZ', start_year=str(datetime.datetime.now().year - 2))
    print()

    # ---------- 4. 获取个股资金流 ----------
    print("【4】获取个股资金流（最近5日）")
    end_d = datetime.datetime.now().strftime('%Y%m%d')
    start_d = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime('%Y%m%d')
    # 手动构造个股资金流
    try:
        data = ak.stock_individual_fund_flow(stock='000564', market='sz')
        print(f"000564.SZ 个股资金流：{len(data)} 条")
        print(data.tail(5)[['日期', '收盘价', '主力净流入-净额', '主力净流入-净占比']].to_string(index=False))
    except Exception as e:
        print(f"获取资金流失败：{e}")
    print()

    # ---------- 5. 获取北向资金 ----------
    print("【5】获取沪深港通资金流向")
    get_hsgt_flow()
    print()

    # ---------- 6. 获取融资融券 ----------
    print("【6】获取融资融券（沪市）")
    get_margin_sh(start_date=start_d, end_date=end_d)
    print()

    # ---------- 7. 获取大盘指数 ----------
    print("【7】获取上证指数日线")
    get_index_daily('000001', start_d, end_d)
    print()

    # ---------- 8. 获取板块 ----------
    print("【8】获取申万行业板块")
    get_board_industry()
    print()

    # ---------- 9. 获取新闻 ----------
    print("【9】获取财经新闻")
    get_news()
    print()

    print("===== akshare 示例完成 =====")


if __name__ == "__main__":
    main()
