#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时基金数据获取与分析系统
基于akshare获取实时基金数据，支持Web展示和定投回测
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RealtimeFundAnalyzer:
    """实时基金分析器"""
    
    def __init__(self):
        """初始化"""
        self.fund_cache = {}
        
    def get_fund_list(self):
        """获取基金列表"""
        try:
            # 使用akshare获取基金列表
            fund_list = ak.fund_name_em()
            return fund_list
        except Exception as e:
            print(f"获取基金列表失败: {e}")
            return pd.DataFrame()
    
    def get_fund_history(self, fund_code, start_date=None, end_date=None):
        """获取基金历史净值数据"""
        try:
            # 使用fund_open_fund_info_em接口获取基金历史净值
            fund_history = ak.fund_open_fund_info_em(
                symbol=fund_code,
                indicator="单位净值走势"
            )
            
            if not fund_history.empty:
                fund_history['净值日期'] = pd.to_datetime(fund_history['净值日期'])
                fund_history = fund_history.sort_values('净值日期')
                
                # 过滤日期范围
                if start_date and end_date:
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date)
                    fund_history = fund_history[
                        (fund_history['净值日期'] >= start_dt) & 
                        (fund_history['净值日期'] <= end_dt)
                    ]
                
            return fund_history
            
        except Exception as e:
            print(f"获取基金{fund_code}历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_fund_basic_info(self, fund_code):
        """获取基金基本信息"""
        try:
            # 获取基金基本信息
            fund_info = ak.fund_name_em()
            fund_data = fund_info[fund_info['基金代码'] == fund_code]
            
            if not fund_data.empty:
                fund_name = str(fund_data.iloc[0]['基金简称'])
                fund_type = str(fund_data.iloc[0]['基金类型'])
                
                # 获取最新净值信息
                try:
                    # 获取最新净值
                    latest_data = ak.fund_open_fund_info_em(
                        symbol=fund_code,
                        indicator="单位净值走势"
                    )
                    
                    if not latest_data.empty:
                        latest = latest_data.iloc[-1]
                        return {
                            'fund_code': fund_code,
                            'fund_name': fund_name,
                            'latest_nav': float(latest['单位净值']),
                            'nav_date': str(latest['净值日期']),
                            'daily_change': float(latest['日增长率']) if '日增长率' in latest else 0,
                            'fund_type': fund_type,
                            'establish_date': '',
                            'fund_size': ''
                        }
                except Exception as e:
                    print(f"获取最新净值失败: {e}")
            
            return {
                'fund_code': fund_code,
                'fund_name': fund_code,
                'latest_nav': 0,
                'nav_date': '',
                'daily_change': 0,
                'fund_type': '未知',
                'establish_date': '',
                'fund_size': ''
            }
            
        except Exception as e:
            print(f"获取基金{fund_code}基本信息失败: {e}")
            return None
    
    def calculate_dca_backtest(self, fund_code, start_date, end_date, 
                             investment_amount=1000, frequency='weekly'):
        """定投回测计算"""
        try:
            # 获取历史数据
            fund_data = self.get_fund_history(fund_code, start_date, end_date)
            
            if fund_data.empty:
                return None
                
            # 数据预处理
            fund_data = fund_data.sort_values('净值日期')
            
            # 定投计算
            if frequency == 'daily':
                dates = pd.date_range(start=start_date, end=end_date, freq='D')
            elif frequency == 'weekly':
                dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')
            else:  # monthly
                dates = pd.date_range(start=start_date, end=end_date, freq='MS')
            
            # 过滤交易日
            trade_dates = fund_data['净值日期'].dt.date.unique()
            investment_dates = [d for d in dates if d.date() in trade_dates]
            
            # 计算定投结果
            results = []
            total_shares = 0
            total_investment = 0
            
            for date in investment_dates:
                # 找到最近的交易日的净值
                nav_data = fund_data[fund_data['净值日期'] <= date].iloc[-1]
                nav = nav_data['单位净值']
                
                shares = investment_amount / nav
                total_shares += shares
                total_investment += investment_amount
                
                current_value = total_shares * nav
                total_return = (current_value - total_investment) / total_investment
                
                results.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'nav': float(nav),
                    'shares': float(shares),
                    'total_shares': float(total_shares),
                    'total_investment': float(total_investment),
                    'current_value': float(current_value),
                    'total_return': float(total_return)
                })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"定投回测计算失败: {e}")
            return None
    
    def search_funds(self, keyword, limit=10):
        """搜索基金"""
        try:
            fund_list = self.get_fund_list()
            if fund_list.empty:
                return pd.DataFrame()
                
            # 按关键词筛选
            mask = fund_list['基金简称'].str.contains(keyword, na=False) | \
                   fund_list['基金代码'].str.contains(keyword, na=False)
            result = fund_list[mask].head(limit)
            
            return result[['基金代码', '基金简称', '基金类型']]
            
        except Exception as e:
            print(f"搜索基金失败: {e}")
            return pd.DataFrame()
    
    def get_fund_performance(self, fund_code, period='1y'):
        """获取基金表现数据"""
        try:
            # 根据时间段设置开始日期
            end_date = datetime.now()
            if period == '1y':
                start_date = end_date - timedelta(days=365)
            elif period == '6m':
                start_date = end_date - timedelta(days=180)
            elif period == '3m':
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # 获取历史数据
            fund_data = self.get_fund_history(
                fund_code, 
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
            
            if fund_data.empty:
                return None
            
            # 计算表现指标
            fund_data = fund_data.sort_values('净值日期')
            start_nav = fund_data['单位净值'].iloc[0]
            end_nav = fund_data['单位净值'].iloc[-1]
            
            total_return = (end_nav - start_nav) / start_nav
            
            # 计算年化收益
            days = (fund_data['净值日期'].iloc[-1] - fund_data['净值日期'].iloc[0]).days
            annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
            
            # 计算波动率
            returns = fund_data['单位净值'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0
            
            # 计算最大回撤
            cumulative = fund_data['单位净值']
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            return {
                'fund_code': fund_code,
                'period': period,
                'total_return': float(total_return),
                'annual_return': float(annual_return),
                'volatility': float(volatility),
                'max_drawdown': float(max_drawdown),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'data_points': len(fund_data)
            }
            
        except Exception as e:
            print(f"获取基金表现数据失败: {e}")
            return None

# 测试代码
if __name__ == "__main__":
    analyzer = RealtimeFundAnalyzer()
    
    print("🚀 测试实时基金数据获取...")
    
    # 测试搜索基金
    search_result = analyzer.search_funds("沪深300", limit=5)
    if not search_result.empty:
        print("✅ 搜索沪深300基金结果:")
        print(search_result)
    
    # 测试获取基金信息
    test_fund = "000001"  # 华夏成长混合
    fund_info = analyzer.get_fund_basic_info(test_fund)
    if fund_info:
        print(f"\n✅ 基金{test_fund}基本信息:")
        print(fund_info)
    
    # 测试获取历史数据
    fund_history = analyzer.get_fund_history(test_fund, 
                                           start_date="20240101",
                                           end_date="20240718")
    if not fund_history.empty:
        print(f"\n✅ 基金{test_fund}历史数据:")
        print(f"数据条数: {len(fund_history)}")
        print(f"最新净值: {fund_history['单位净值'].iloc[-1]}")
        print(f"日期范围: {fund_history['净值日期'].min()} - {fund_history['净值日期'].max()}")
    
    # 测试定投回测
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 7, 18)
    dca_result = analyzer.calculate_dca_backtest(
        test_fund, start_date, end_date, 
        investment_amount=1000, frequency='weekly'
    )
    
    if dca_result is not None and not dca_result.empty:
        print(f"\n✅ 定投回测结果:")
        print(f"总投资金额: ¥{dca_result['total_investment'].iloc[-1]:,.2f}")
        print(f"当前价值: ¥{dca_result['current_value'].iloc[-1]:,.2f}")
        print(f"总收益率: {dca_result['total_return'].iloc[-1]*100:.2f}%")
        print("最近5次定投:")
        print(dca_result.tail()[['date', 'nav', 'total_return']])
    
    # 测试基金表现
    performance = analyzer.get_fund_performance(test_fund, period='6m')
    if performance:
        print(f"\n✅ 基金表现(6个月):")
        print(f"总收益: {performance['total_return']*100:.2f}%")
        print(f"年化收益: {performance['annual_return']*100:.2f}%")
        print(f"最大回撤: {abs(performance['max_drawdown'])*100:.2f}%")
        print(f"波动率: {performance['volatility']*100:.2f}%")
