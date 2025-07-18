#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel部署版本的基金智能分析Web应用
精简版本，减少依赖包大小
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import requests

# 创建Flask应用
app = Flask(__name__)

# 模拟数据（实际部署时可替换为真实API）
MOCK_FUNDS = [
    {"基金代码": "000051", "基金简称": "华夏沪深300ETF联接A", "基金类型": "指数型"},
    {"基金代码": "110020", "基金简称": "易方达沪深300ETF联接A", "基金类型": "指数型"},
    {"基金代码": "001630", "基金简称": "天弘中证500指数A", "基金类型": "指数型"},
    {"基金代码": "001594", "基金简称": "天弘中证银行指数A", "基金类型": "指数型"},
    {"基金代码": "001550", "基金简称": "天弘上证50指数A", "基金类型": "指数型"}
]

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/search_funds')
def search_funds():
    """搜索基金API"""
    keyword = request.args.get('keyword', '')
    limit = int(request.args.get('limit', 10))
    
    if not keyword:
        return jsonify([])
    
    # 模拟搜索
    results = [f for f in MOCK_FUNDS if keyword in f['基金简称'] or keyword in f['基金代码']]
    return jsonify(results[:limit])

@app.route('/api/fund_info/<fund_code>')
def get_fund_info(fund_code):
    """获取基金基本信息"""
    fund = next((f for f in MOCK_FUNDS if f['基金代码'] == fund_code), None)
    if not fund:
        return jsonify({})
    
    # 模拟基金信息
    return jsonify({
        "fund_code": fund_code,
        "fund_name": fund['基金简称'],
        "fund_type": fund['基金类型'],
        "latest_nav": 1.2345,
        "daily_change": 0.56,
        "nav_date": datetime.now().strftime('%Y-%m-%d')
    })

@app.route('/api/fund_history/<fund_code>')
def get_fund_history(fund_code):
    """获取基金历史数据"""
    # 模拟历史数据
    import random
    from datetime import datetime, timedelta
    
    days = 365
    data = []
    base_nav = 1.0
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        change = random.uniform(-0.02, 0.02)
        base_nav *= (1 + change)
        
        data.append({
            "净值日期": date.strftime('%Y-%m-%d'),
            "单位净值": round(base_nav, 4),
            "累计净值": round(base_nav * 1.5, 4)
        })
    
    return jsonify(data)

@app.route('/api/dca_backtest', methods=['POST'])
def dca_backtest():
    """定投回测API"""
    try:
        data = request.json
        
        fund_code = data.get('fund_code')
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        investment_amount = float(data.get('investment_amount', 1000))
        frequency = data.get('frequency', 'weekly')
        
        # 模拟回测计算
        import random
        
        # 计算投资期数
        days_diff = (end_date - start_date).days
        if frequency == 'daily':
            periods = days_diff
        elif frequency == 'weekly':
            periods = days_diff // 7
        else:  # monthly
            periods = days_diff // 30
        
        periods = max(1, periods)
        
        # 模拟收益
        total_investment = investment_amount * periods
        random_return = random.uniform(-0.2, 0.5)  # -20% 到 50% 的随机收益
        current_value = total_investment * (1 + random_return)
        total_profit = current_value - total_investment
        
        # 生成详细数据
        data_points = []
        current_value_acc = 0
        for i in range(periods):
            date = start_date + timedelta(days=i*7 if frequency == 'weekly' else i*30 if frequency == 'monthly' else i)
            shares = investment_amount / (1.0 + random.uniform(-0.1, 0.1))
            current_value_acc += shares
            data_points.append({
                "date": date.strftime('%Y-%m-%d'),
                "nav": round(1.0 + random.uniform(-0.1, 0.1), 4),
                "shares": round(shares, 2),
                "total_investment": investment_amount * (i+1),
                "current_value": round(current_value_acc * (1 + random_return * (i+1)/periods), 2),
                "total_return": round(random_return * (i+1)/periods, 4)
            })
        
        return jsonify({
            'data': data_points,
            'summary': {
                'total_investment': round(total_investment, 2),
                'current_value': round(current_value, 2),
                'total_return': round(random_return, 4),
                'total_profit': round(total_profit, 2)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fund_performance/<fund_code>')
def get_performance(fund_code):
    """获取基金表现数据"""
    # 模拟表现数据
    return jsonify({
        "fund_code": fund_code,
        "total_return": 0.1234,
        "annual_return": 0.1234,
        "max_drawdown": -0.089,
        "volatility": 0.1567,
        "sharpe_ratio": 0.789
    })

@app.route('/api/chart_data/<fund_code>')
def get_chart_data(fund_code):
    """获取图表数据"""
    # 模拟图表数据
    import random
    from datetime import datetime, timedelta
    
    data = []
    base_nav = 1.0
    
    for i in range(365):
        date = datetime.now() - timedelta(days=365-i)
        change = random.uniform(-0.02, 0.02)
        base_nav *= (1 + change)
        data.append({
            "x": date.strftime('%Y-%m-%d'),
            "y": round(base_nav, 4)
        })
    
    return jsonify({
        'chart': json.dumps({
            "data": [{
                "x": [d["x"] for d in data],
                "y": [d["y"] for d in data],
                "type": "scatter",
                "mode": "lines",
                "name": "单位净值",
                "line": {"color": "#1e40af", "width": 2}
            }],
            "layout": {
                "title": "基金净值走势",
                "xaxis": {"title": "日期"},
                "yaxis": {"title": "单位净值"},
                "hovermode": "x unified"
            }
        })
    })

@app.route('/api/ai_analysis', methods=['POST'])
def ai_analysis():
    """AI智能分析API"""
    try:
        data = request.json
        
        fund_info = data.get('fund_info', {})
        dca_result = data.get('dca_result', {})
        performance = data.get('performance', {})
        
        # 模拟AI分析
        analysis = f"""## 基金定投策略分析

### 综合评价
{fund_info.get('fund_name', '该基金')}在过去的表现中展现了{performance.get('total_return', 0)*100:.1f}%的总收益，年化收益{performance.get('annual_return', 0)*100:.1f}%。

### 定投回测结果
- 总投资金额：¥{dca_result.get('total_investment', 0):,.0f}
- 当前价值：¥{dca_result.get('current_value', 0):,.0f}
- 总收益：¥{dca_result.get('total_profit', 0):,.0f}
- 总收益率：{dca_result.get('total_return', 0)*100:.2f}%

### 风险提示
最大回撤为{abs(performance.get('max_drawdown', 0))*100:.1f}%，波动率为{performance.get('volatility', 0)*100:.1f}%，建议投资者根据自身风险承受能力谨慎投资。

### 投资建议
适合长期定投，建议持有期3年以上，分批建仓降低风险。

### 适合投资者类型
- 风险承受能力中等以上的投资者
- 追求稳健增长的长期投资者
- 有一定投资经验的定投用户
"""
        
        return jsonify({'analysis': analysis})
        
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

# Vercel入口点
if __name__ == '__main__':
    # 本地测试
    app.run(debug=True, host='0.0.0.0', port=8080)
else:
    # Vercel生产环境
    app.config['DEBUG'] = False
