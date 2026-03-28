#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "tushare",
#     "pandas",
# ]
# ///
# -*- coding: utf-8 -*-
"""
tushare 股票数据获取完整示例脚本

覆盖：行情、财务、资金流、基础数据、板块指数、融资融券、龙虎榜、宏观数据、新闻公告
使用 uv run scripts/stock_data_demo.py 执行
"""

import os
import tushare as ts

# ---------- 环境变量校验 ----------
token = os.getenv("TUSHARE_TOKEN")
api_url = os.getenv("TUSHARE_URL")

missing = []
if not token:
    missing.append("TUSHARE_TOKEN")
if not api_url:
    missing.append("TUSHARE_URL")

if missing:
    raise RuntimeError(
        f"缺少必需的环境变量: {', '.join(missing)}\n"
        "请在运行前设置：\n"
        "  export TUSHARE_TOKEN=你的Token\n"
        "  export TUSHARE_URL=http://118.89.66.41:8010/\n"
        "（Token 获取：https://tushare.pro/register）"
    )

import pandas as pd

# ---------- 初始化 pro 接口 ----------
pro = ts.pro_api(token)
pro._DataApi__http_url = api_url


# =============================================================================
# 行情数据
# =============================================================================

def get_stock_list(exchange="", list_status="L"):
    """
    获取 A股股票列表
    参数：
        exchange: 交易所，SSE/SZSE/BSE，默认全市场
        list_status: L=上市 D=退市 P=暂停上市
    返回：DataFrame，字段 ts_code/symbol/name/area/industry/list_date
    """
    try:
        data = pro.stock_basic(exchange=exchange, list_status=list_status,
                               fields='ts_code,symbol,name,area,industry,list_date')
        print(f"股票列表获取成功：{len(data)} 只")
        print(data.head(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取股票列表失败：{e}")
        return None


def get_daily_data(ts_code, start_date, end_date):
    """
    获取日线数据（前复权）
    参数：ts_code 如 '000564.SZ'，日期 YYYYMMDD
    返回：DataFrame，字段 date/ts_code/open/high/low/close/vol/amount/pct_chg
    """
    try:
        data = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        print(f"{ts_code} 日线数据获取成功：{len(data)} 条")
        print(data.head(5)[['trade_date', 'open', 'high', 'low', 'close', 'vol']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取日线数据失败：{e}")
        return None


def get_weekly_data(ts_code, start_date, end_date):
    """
    获取周线数据
    """
    try:
        data = pro.weekly(ts_code=ts_code, start_date=start_date, end_date=end_date)
        print(f"{ts_code} 周线数据获取成功：{len(data)} 条")
        print(data.head(3).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取周线数据失败：{e}")
        return None


def get_monthly_data(ts_code, start_date, end_date):
    """
    获取月线数据
    """
    try:
        data = pro.monthly(ts_code=ts_code, start_date=start_date, end_date=end_date)
        print(f"{ts_code} 月线数据获取成功：{len(data)} 条")
        print(data.head(3).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取月线数据失败：{e}")
        return None


def get_adj_factor(ts_code, start_date, end_date):
    """
    获取复权因子
    """
    try:
        data = pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)
        print(f"{ts_code} 复权因子获取成功：{len(data)} 条")
        print(data.tail(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取复权因子失败：{e}")
        return None


def get_daily_basic(ts_code, start_date, end_date):
    """
    获取每日基本面指标（PE/PS/PB/换手率/流通市值等）
    """
    try:
        data = pro.daily_basic(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                fields='ts_code,trade_date,close,pe_ttm,pb,ps_ttm,total_share,float_share,free_share,total_mv,circ_mv,turnover_rate,turnover_rate_f,pe_ttm_listed')
        print(f"{ts_code} 每日指标获取成功：{len(data)} 条")
        print(data.tail(5)[['trade_date', 'close', 'pe_ttm', 'pb', 'circ_mv', 'turnover_rate']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取每日指标失败：{e}")
        return None


def get_realtime_k(ts_code):
    """
    获取实时日线（单股）
    """
    try:
        data = pro.rt_k(ts_code=ts_code)
        print(f"{ts_code} 实时日线获取成功：{len(data)} 条")
        print(data.head(3).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取实时日线失败：{e}")
        return None


# =============================================================================
# 财务数据
# =============================================================================

def get_income(ts_code, start_year=None, end_year=None):
    """
    获取利润表
    参数：start_year/end_year 格式 YYYY
    返回：DataFrame，含净利润、营业总收入、每股收益等
    """
    try:
        data = pro.income(ts_code=ts_code, start_year=start_year, end_year=end_year,
                          fields='ts_code,ann_date,end_date,report_type,basic_eps,diluted_eps,total_revenue,revenue,total_profit,n_income,n_income_attr_p,parent_netprofit')
        print(f"{ts_code} 利润表获取成功：{len(data)} 条")
        print(data.tail(5)[['end_date', 'total_revenue', 'n_income', 'basic_eps']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取利润表失败：{e}")
        return None


def get_balancesheet(ts_code, start_year=None, end_year=None):
    """
    获取资产负债表
    """
    try:
        data = pro.balancesheet(ts_code=ts_code, start_year=start_year, end_year=end_year,
                                fields='ts_code,ann_date,end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int')
        print(f"{ts_code} 资产负债表获取成功：{len(data)} 条")
        print(data.tail(5)[['end_date', 'total_assets', 'total_liab', 'total_hldr_eqy_exc_min_int']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取资产负债表失败：{e}")
        return None


def get_cashflow(ts_code, start_year=None, end_year=None):
    """
    获取现金流量表
    """
    try:
        data = pro.cashflow(ts_code=ts_code, start_year=start_year, end_year=end_year,
                            fields='ts_code,ann_date,end_date,net_profit,n_cashflow_act,stot_inflows_inv_act,n_cashflow_inv_act,n_cash_flows_fnc_act')
        print(f"{ts_code} 现金流量表获取成功：{len(data)} 条")
        print(data.tail(5)[['end_date', 'net_profit', 'n_cashflow_act', 'n_cashflow_inv_act']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取现金流量表失败：{e}")
        return None


def get_fina_indicator(ts_code, start_year=None, quarter=None):
    """
    获取财务指标（ROE/毛利率/净利率/资产负债率/每股收益等）
    参数：start_year 格式 YYYY，quarter 1-4
    """
    try:
        if start_year and quarter:
            data = pro.fina_indicator(ts_code=ts_code, start_year=start_year, quarter=quarter,
                                      fields='ts_code,ann_date,end_date,roe,roe_yearly,grossprofit_margin,netprofit_margin,debt_to_assets,eps,bps')
        else:
            data = pro.fina_indicator(ts_code=ts_code, limit=20,
                                      fields='ts_code,ann_date,end_date,roe,grossprofit_margin,netprofit_margin,debt_to_assets,eps,bps')
        print(f"{ts_code} 财务指标获取成功：{len(data)} 条")
        print(data.tail(5)[['end_date', 'roe', 'grossprofit_margin', 'netprofit_margin', 'eps']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取财务指标失败：{e}")
        return None


def get_forecast(ts_code, start_year=None):
    """
    获取业绩预告/业绩快报
    """
    try:
        if start_year:
            data = pro.forecast(ts_code=ts_code, start_year=start_year,
                                fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max,revenue_min,revenue_max,profit_min,profit_max')
        else:
            data = pro.forecast(ts_code=ts_code,
                                fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max,revenue_min,revenue_max')
        print(f"{ts_code} 业绩预告获取成功：{len(data)} 条")
        print(data.head(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取业绩预告失败：{e}")
        return None


def get_express(ts_code, start_year=None):
    """
    获取业绩快报
    """
    try:
        if start_year:
            data = pro.express(ts_code=ts_code, start_year=start_year,
                               fields='ts_code,ann_date,end_date,revenue,profit,asset,equity,eps,bps')
        else:
            data = pro.express(ts_code=ts_code,
                               fields='ts_code,ann_date,end_date,revenue,profit,eps')
        print(f"{ts_code} 业绩快报获取成功：{len(data)} 条")
        print(data.head(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取业绩快报失败：{e}")
        return None


def get_fina_mainbz(ts_code):
    """
    获取主营业务构成（按行业/产品/地区）
    """
    try:
        data = pro.fina_mainbz(ts_code=ts_code,
                                fields='ts_code,ann_date,end_date,bz_item,bz_ratio,收入构成')
        print(f"{ts_code} 主营业务构成获取成功：{len(data)} 条")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取主营业务构成失败：{e}")
        return None


def get_dividend(ts_code):
    """
    获取分红送股数据
    """
    try:
        data = pro.dividend(ts_code=ts_code,
                            fields='ts_code,ann_date,div_listed_date,stk_div_amt,stk_bo_rate,stk_co_rate')
        print(f"{ts_code} 分红送股获取成功：{len(data)} 条")
        print(data.head(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取分红送股失败：{e}")
        return None


# =============================================================================
# 资金流向
# =============================================================================

def get_moneyflow(ts_code, start_date, end_date):
    """
    获取个股资金流向（大单小单）
    """
    try:
        data = pro.moneyflow(ts_code=ts_code, start_date=start_date, end_date=end_date,
                             fields='ts_code,trade_date,buy_sm_amount,buy_sm_vol,sell_sm_amount,sell_sm_vol,buy_md_amount,buy_md_vol,sell_md_amount,sell_md_vol,buy_lg_amount,buy_lg_vol,sell_lg_amount,sell_lg_vol,buy_elg_amount,buy_elg_vol,sell_elg_amount,sell_elg_vol,net_mf_amount')
        print(f"{ts_code} 资金流向获取成功：{len(data)} 条")
        print(data.tail(5)[['trade_date', 'buy_lg_amount', 'sell_lg_amount', 'net_mf_amount']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取资金流向失败：{e}")
        return None


def get_moneyflow_hsgt(start_date, end_date):
    """
    获取沪深港通资金流向（北向资金）
    """
    try:
        data = pro.moneyflow_hsgt(start_date=start_date, end_date=end_date,
                                   fields='trade_date,ggt_ss,ggt_sz,hgt,sgt,north_money,south_money')
        print(f"沪深港通资金流向获取成功：{len(data)} 条")
        print(data.tail(10)[['trade_date', 'hgt', 'sgt', 'north_money']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取北向资金失败：{e}")
        return None


def get_hsgt_top10(trade_date, market="SH"):
    """
    获取沪深港通个股十大成交
    参数：trade_date YYYYMMDD，market SH/SZ/HK
    """
    try:
        data = pro.hsgt_top10(ts_code=None, trade_date=trade_date, market=market,
                              fields='trade_date,ts_code,symbol,name,close,pct_change,buy_amount,sell_amount,net_amount')
        print(f"{market} {trade_date} 沪深港通个股Top10获取成功：{len(data)} 条")
        print(data.to_string(index=False))
        return data
    except Exception as e:
        print(f"获取沪深港通Top10失败：{e}")
        return None


# =============================================================================
# 基础数据
# =============================================================================

def get_stock_company(ts_code):
    """
    获取上市公司基本信息
    """
    try:
        data = pro.stock_company(ts_code=ts_code,
                                 fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,website,email,office')
        print(f"{ts_code} 公司信息获取成功")
        print(data.T.to_string())
        return data
    except Exception as e:
        print(f"获取公司信息失败：{e}")
        return None


def get_stk_holdernumber(ts_code, start_date, end_date):
    """
    获取股东人数（变化）
    """
    try:
        data = pro.stk_holdernumber(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                    fields='TS_CODE,ANN_DATE,END_DATE,HOLDER_NUM')
        print(f"{ts_code} 股东人数获取成功：{len(data)} 条")
        print(data.tail(10)[['END_DATE', 'HOLDER_NUM']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取股东人数失败：{e}")
        return None


def get_top10_holders(ts_code, start_date, end_date):
    """
    获取前十大股东
    """
    try:
        data = pro.top10_holders(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                 fields='ts_code,ann_date,end_date,holder_name,hold_amount,hold_ratio')
        print(f"{ts_code} 前十大股东获取成功：{len(data)} 条")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取前十大股东失败：{e}")
        return None


# =============================================================================
# 板块指数
# =============================================================================

def get_index_list():
    """
    获取指数列表
    """
    try:
        data = pro.index_basic(ts_code=None, name=None,
                               fields='ts_code,name,fullname,category,base_date,base_point')
        print(f"指数列表获取成功：{len(data)} 只")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取指数列表失败：{e}")
        return None


def get_index_daily(index_code, start_date, end_date):
    """
    获取指数日线
    参数：index_code 如 '000001.SH'（上证指数）
    """
    try:
        data = pro.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date,
                               fields='ts_code,trade_date,open,high,low,close,vol,amount,pct_chg')
        print(f"{index_code} 指数日线获取成功：{len(data)} 条")
        print(data.tail(5)[['trade_date', 'open', 'close', 'pct_chg']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取指数日线失败：{e}")
        return None


def get_sw_daily(index_code, start_date, end_date):
    """
    获取申万行业指数日线
    """
    try:
        data = pro.sw_daily(ts_code=index_code, start_date=start_date, end_date=end_date,
                            fields='ts_code,trade_date,open,close,pct_change')
        print(f"{index_code} 申万行业指数日线获取成功：{len(data)} 条")
        print(data.tail(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取申万指数日线失败：{e}")
        return None


def get_index_classify(level="L1"):
    """
    获取申万行业分类
    参数：level L1/L2/L3
    """
    try:
        data = pro.index_classify(level=level,
                                  fields='index_code,industry_code,industry_name,level,src')
        print(f"申万行业分类（{level}）获取成功：{len(data)} 条")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取申万分类失败：{e}")
        return None


def get_index_member(index_code):
    """
    获取申万行业成分股
    """
    try:
        data = pro.index_member_all(index_code=index_code,
                                    fields='index_code,index_name,in_code,in_name,is_new')
        print(f"{index_code} 成分股获取成功：{len(data)} 条")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取成分股失败：{e}")
        return None


def get_ths_index():
    """
    获取同花顺概念板块
    """
    try:
        data = pro.ths_index(body="D", type="N",
                             fields='ts_code,name,count,change,volume,amount')
        print(f"同花顺概念板块获取成功：{len(data)} 条")
        print(data[['ts_code', 'name', 'count', 'exchange']].head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取同花顺板块失败：{e}")
        return None


def get_ths_member(ths_code):
    """
    获取同花顺概念板块成分股
    """
    try:
        data = pro.ths_member(ts_code=ths_code,
                              fields='ts_code,name,code')
        print(f"{ths_code} 成分股获取成功：{len(data)} 条")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取同花顺成分股失败：{e}")
        return None


# =============================================================================
# 融资融券
# =============================================================================

def get_margin(trade_date):
    """
    获取融资融券汇总
    参数：trade_date YYYYMMDD
    """
    try:
        data = pro.margin(trade_date=trade_date,
                          fields='trade_date,exchange,sec_code,sec_name,new_balance,balance,buy_balance,repay_balance')
        print(f"融资融券汇总 {trade_date} 获取成功：{len(data)} 条")
        print(data.head(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取融资融券失败：{e}")
        return None


def get_margin_detail(ts_code, start_date, end_date):
    """
    获取融资融券明细
    """
    try:
        data = pro.margin_detail(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                fields='TS_CODE,TRADE_DATE,RZYE,RZRQYE,RZMRE,RZCHE')
        print(f"{ts_code} 融资融券明细获取成功：{len(data)} 条")
        print(data.tail(5)[['TRADE_DATE', 'RZYE', 'RZRQYE', 'RZMRE']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取融资融券明细失败：{e}")
        return None


# =============================================================================
# 龙虎榜
# =============================================================================

def get_top_list(trade_date):
    """
    获取龙虎榜每日明细
    """
    try:
        data = pro.top_list(trade_date=trade_date,
                            fields='trade_date,ts_code,name,close,pct_change,turnover_rate,amount,reason')
        print(f"{trade_date} 龙虎榜获取成功：{len(data)} 条")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取龙虎榜失败：{e}")
        return None


def get_top_inst(trade_date):
    """
    获取龙虎榜机构明细
    """
    try:
        data = pro.top_inst(trade_date=trade_date,
                            fields='trade_date,ts_code,name,side,buy_amount,sell_amount')
        print(f"{trade_date} 龙虎榜机构明细获取成功：{len(data)} 条")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取龙虎榜机构明细失败：{e}")
        return None


# =============================================================================
# 宏观数据
# =============================================================================

def get_cn_gdp(quarter=None):
    """
    获取 GDP 数据
    """
    try:
        data = pro.cn_gdp(q=quarter,
                          fields='quarter,gdp_yoy,gdp_total,gdp_origin')
        print(f"GDP 数据获取成功：{len(data)} 条")
        print(data.tail(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取GDP数据失败：{e}")
        return None


def get_cn_cpi(month=None):
    """
    获取 CPI 数据
    """
    try:
        data = pro.cn_cpi(m=month,
                          fields='month,ym_last_year,ym_last_month,ym_same_period_last_year')
        print(f"CPI 数据获取成功：{len(data)} 条")
        print(data.tail(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取CPI数据失败：{e}")
        return None


def get_cn_ppi(month=None):
    """
    获取 PPI 数据
    """
    try:
        data = pro.cn_ppi(m=month,
                          fields='month,ppi_yoy,ppi_month,ppi_last_month')
        print(f"PPI 数据获取成功：{len(data)} 条")
        print(data.tail(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取PPI数据失败：{e}")
        return None


def get_cn_pmi(month=None):
    """
    获取 PMI 数据
    """
    try:
        data = pro.cn_pmi(m=month)
        print(f"PMI 数据获取成功：{len(data)} 条")
        print(data[['MONTH']].tail(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取PMI数据失败：{e}")
        return None


def get_sf_month(start_date, end_date):
    """
    获取社会融资数据（月度）
    """
    try:
        data = pro.sf_month(start_date=start_date, end_date=end_date,
                            fields='month,inc_month,inc_cumval,stk_endval')
        print(f"社融数据获取成功：{len(data)} 条")
        print(data.tail(10)[['month', 'inc_month', 'inc_cumval']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取社融数据失败：{e}")
        return None


def get_cn_m(start_date, end_date):
    """
    获取货币供应量（M0/M1/M2）
    """
    try:
        data = pro.cn_m(start_date=start_date, end_date=end_date,
                        fields='month,m0,m0_yoy,m1,m1_yoy,m2,m2_yoy')
        print(f"货币供应量获取成功：{len(data)} 条")
        print(data.tail(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取货币供应量失败：{e}")
        return None


def get_shibor(start_date=None, end_date=None):
    """
    获取 Shibor 利率
    """
    try:
        data = pro.shibor(start_date=start_date, end_date=end_date,
                          fields='date,on,1w,2w,1m,3m,6m,9m,1y')
        print(f"Shibor 利率获取成功：{len(data)} 条")
        print(data.tail(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取Shibor失败：{e}")
        return None


def get_shibor_lpr():
    """
    获取 LPR 贷款基础利率
    """
    try:
        data = pro.shibor_lpr()
        print(f"LPR 利率获取成功：{len(data)} 条")
        print(data[['date', '1y', '5y']].tail(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取LPR失败：{e}")
        return None


# =============================================================================
# 新闻公告
# =============================================================================

def get_news(start_date=None, end_date=None):
    """
    获取新闻快讯
    """
    try:
        data = pro.news(src="eastmoney", start_date=start_date, end_date=end_date,
                        fields='datetime,title,content,channel')
        print(f"财经新闻获取成功：{len(data)} 条")
        print(data[['datetime', 'title']].head(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取新闻失败：{e}")
        return None


def get_cctv_news():
    """
    获取新闻联播文字稿
    """
    try:
        data = pro.cctv_news(limit=20)
        print(f"新闻联播获取成功：{len(data)} 条")
        print(data[['date', 'title']].head(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取新闻联播失败：{e}")
        return None


def get_anns_d(ts_code, start_date, end_date):
    """
    获取上市公司公告
    """
    try:
        data = pro.anns_d(ts_code=ts_code, start_date=start_date, end_date=end_date,
                          fields='ts_code,ann_date,title,category,page_no')
        print(f"{ts_code} 公告获取成功：{len(data)} 条")
        print(data[['ann_date', 'title', 'category']].head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取公告失败：{e}")
        return None


def get_research_report(ts_code=None, start_date=None, end_date=None):
    """
    获取券商研究报告
    """
    try:
        data = pro.research_report(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                   fields='ts_code,title,publish_date,meeting_type,org_name')
        print(f"券商研报获取成功：{len(data)} 条")
        print(data[['publish_date', 'title', 'org_name']].head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取券商研报失败：{e}")
        return None


# =============================================================================
# 新股数据
# =============================================================================

def get_new_share():
    """
    获取新股上市数据
    """
    try:
        data = pro.new_share(start_date=None, end_date=None,
                             fields='ts_code,name,issue_date,ipo_date,price,pe,amount,limit_amount,funds')
        print(f"新股列表获取成功：{len(data)} 条")
        print(data[['name', 'issue_date', 'price', 'pe']].head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取新股数据失败：{e}")
        return None


# =============================================================================
# ST / 涨跌停
# =============================================================================

def get_st():
    """
    获取 ST 风险警示股票列表
    """
    try:
        data = pro.st()
        print(f"ST股票列表获取成功：{len(data)} 条")
        print(data.head(10).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取ST列表失败：{e}")
        return None


def get_limit_list_d(trade_date):
    """
    获取涨跌停、炸板数据
    """
    try:
        data = pro.limit_list_d(trade_date=trade_date, limit=100,
                                 fields='trade_date,ts_code,name,close,pct_chg,amount,limit_amount,turnover_ratio,open_times,up_stat,limit')
        print(f"{trade_date} 涨跌停数据获取成功：{len(data)} 条")
        print(data[data['up_stat'].isin(['涨停', '炸板'])].head(10)[['ts_code', 'name', 'close', 'pct_chg', 'up_stat']].to_string(index=False))
        return data
    except Exception as e:
        print(f"获取涨跌停数据失败：{e}")
        return None


# =============================================================================
# 交易日期
# =============================================================================

def get_trade_cal(start_date, end_date, exchange="SSE"):
    """
    获取交易日历
    """
    try:
        data = pro.trade_cal(start_date=start_date, end_date=end_date, exchange=exchange,
                             fields='exchange,cal_date,is_open,pretrade_date')
        print(f"交易日历（{exchange}）获取成功：{len(data)} 条")
        print(data[data['is_open'] == '1'].tail(5).to_string(index=False))
        return data
    except Exception as e:
        print(f"获取交易日历失败：{e}")
        return None


# =============================================================================
# 主函数演示
# =============================================================================

def main():
    """
    演示所有数据获取接口
    """
    print("===== tushare 完整数据获取示例 =====\n")

    import datetime
    today = datetime.datetime.now()
    end_date = today.strftime('%Y%m%d')
    start_30d = (today - datetime.timedelta(days=30)).strftime('%Y%m%d')
    start_y = (today - datetime.timedelta(days=365)).strftime('%Y%m%d')
    last_year = str(today.year - 1)

    # 以供销大集（000564.SZ）为例
    ts_code = "000564.SZ"
    print(f"示例股票：{ts_code}\n")

    # --- 行情数据 ---
    print("【行情数据】")
    get_stock_list(list_status="L")
    print()
    get_daily_data(ts_code, start_30d, end_date)
    print()

    # --- 财务数据 ---
    print("【财务数据】")
    get_income(ts_code, start_year=last_year)
    print()
    get_balancesheet(ts_code, start_year=last_year)
    print()
    get_cashflow(ts_code, start_year=last_year)
    print()
    get_fina_indicator(ts_code, start_year=last_year, quarter=4)
    print()
    get_fina_mainbz(ts_code)
    print()

    # --- 资金流向 ---
    print("【资金流向】")
    get_moneyflow(ts_code, start_30d, end_date)
    print()
    get_moneyflow_hsgt(start_30d, end_date)
    print()

    # --- 板块指数 ---
    print("【板块指数】")
    get_index_list()
    print()
    get_index_daily("000001.SH", start_30d, end_date)
    print()
    get_index_classify("L1")
    print()

    # --- 融资融券 ---
    print("【融资融券】")
    recent_trade = pro.trade_cal(start_date=end_date, end_date=end_date, exchange="SSE",
                                   fields='cal_date').iloc[0]['cal_date']
    get_margin(recent_trade)
    print()

    # --- 龙虎榜 ---
    print("【龙虎榜】")
    get_top_list(recent_trade)
    print()
    get_top_inst(recent_trade)
    print()

    # --- 宏观数据 ---
    print("【宏观数据】")
    get_cn_gdp()
    print()
    get_cn_cpi()
    print()
    get_cn_ppi()
    print()
    get_sf_month(start_y[:4] + "01", end_date)
    print()

    # --- 新闻公告 ---
    print("【新闻公告】")
    get_cctv_news()
    print()
    get_anns_d(ts_code, start_y, end_date)
    print()
    get_research_report(ts_code=ts_code, start_date=start_y, end_date=end_date)
    print()

    # --- 新股/ST ---
    print("【新股/ST】")
    get_new_share()
    print()
    get_st()
    print()

    # --- 基础数据 ---
    print("【基础数据】")
    get_stock_company(ts_code)
    print()

    # --- 交易日期 ---
    print("【交易日历】")
    get_trade_cal(start_30d, end_date)
    print()

    print("===== tushare 示例完成 =====")


if __name__ == "__main__":
    main()
