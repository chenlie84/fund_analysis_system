#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金实时分析Web应用
基于Flask的Web界面，支持实时基金数据获取、分析和定投回测
集成Moonshot AI进行智能分析
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from realtime_fund_analyzer import RealtimeFundAnalyzer
import plotly.graph_objs as go
import plotly.utils
import requests

app = Flask(__name__)
analyzer = RealtimeFundAnalyzer()

# Moonshot AI配置
MOONSHOT_API_KEY = os.getenv('MOONSHOT_API_KEY', 'your-moonshot-api-key')
MOONSHOT_API_URL = "https://api.moonshot.cn/v1/chat/completions"

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
    
    result = analyzer.search_funds(keyword, limit)
    return jsonify(result.to_dict('records'))

@app.route('/api/fund_info/<fund_code>')
def get_fund_info(fund_code):
    """获取基金基本信息"""
    info = analyzer.get_fund_basic_info(fund_code)
    return jsonify(info or {})

@app.route('/api/fund_history/<fund_code>')
def get_fund_history(fund_code):
    """获取基金历史数据"""
    start_date = request.args.get('start_date', 
                                (datetime.now() - timedelta(days=365)).strftime('%Y%m%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y%m%d'))
    
    history = analyzer.get_fund_history(fund_code, start_date, end_date)
    return jsonify(history.to_dict('records') if not history.empty else [])

@app.route('/api/dca_backtest', methods=['POST'])
def dca_backtest():
    """定投回测API"""
    data = request.json
    
    fund_code = data.get('fund_code')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
    investment_amount = float(data.get('investment_amount', 1000))
    frequency = data.get('frequency', 'weekly')
    
    result = analyzer.calculate_dca_backtest(
        fund_code, start_date, end_date, 
        investment_amount, frequency
    )
    
    if result is None:
        return jsonify({'error': '无法获取基金数据或计算失败'})
    
    return jsonify({
        'data': result.to_dict('records'),
        'summary': {
            'total_investment': float(result['total_investment'].iloc[-1]),
            'current_value': float(result['current_value'].iloc[-1]),
            'total_return': float(result['total_return'].iloc[-1]),
            'total_profit': float(result['current_value'].iloc[-1] - result['total_investment'].iloc[-1])
        }
    })

@app.route('/api/fund_performance/<fund_code>')
def get_performance(fund_code):
    """获取基金表现数据"""
    period = request.args.get('period', '1y')
    
    performance = analyzer.get_fund_performance(fund_code, period)
    return jsonify(performance or {})

@app.route('/api/chart_data/<fund_code>')
def get_chart_data(fund_code):
    """获取图表数据"""
    start_date = request.args.get('start_date', 
                                (datetime.now() - timedelta(days=365)).strftime('%Y%m%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y%m%d'))
    
    history = analyzer.get_fund_history(fund_code, start_date, end_date)
    
    if history.empty:
        return jsonify({'error': '无数据'})
    
    # 创建图表数据
    nav_trace = go.Scatter(
        x=history['净值日期'].tolist(),
        y=history['单位净值'].tolist(),
        mode='lines',
        name='单位净值',
        line=dict(color='#1f77b4', width=2)
    )
    
    layout = go.Layout(
        title='基金净值走势',
        xaxis=dict(title='日期'),
        yaxis=dict(title='单位净值'),
        hovermode='x unified'
    )
    
    fig = go.Figure(data=[nav_trace], layout=layout)
    
    return jsonify({
        'chart': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    })

@app.route('/api/ai_analysis', methods=['POST'])
def ai_analysis():
    """AI智能分析API"""
    data = request.json
    
    fund_info = data.get('fund_info', {})
    dca_result = data.get('dca_result', {})
    performance = data.get('performance', {})
    
    # 构建分析提示
    prompt = f"""
    请作为专业的基金投资顾问，对以下基金定投回测结果进行深度分析：
    
    基金信息：
    - 基金代码：{fund_info.get('fund_code', '')}
    - 基金名称：{fund_info.get('fund_name', '')}
    - 基金类型：{fund_info.get('fund_type', '')}
    
    定投回测结果：
    - 总投资金额：¥{dca_result.get('total_investment', 0):,.2f}
    - 当前价值：¥{dca_result.get('current_value', 0):,.2f}
    - 总收益：¥{dca_result.get('total_profit', 0):,.2f}
    - 总收益率：{dca_result.get('total_return', 0)*100:.2f}%
    
    基金表现：
    - 总收益：{performance.get('total_return', 0)*100:.2f}%
    - 年化收益：{performance.get('annual_return', 0)*100:.2f}%
    - 最大回撤：{abs(performance.get('max_drawdown', 0))*100:.2f}%
    - 波动率：{performance.get('volatility', 0)*100:.2f}%
    
    请提供：
    1. 对该基金定投策略的综合评价
    2. 风险提示和建议
    3. 未来投资建议
    4. 适合的投资者类型
    
    请用中文回答，语言要专业但易懂。
    """
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {MOONSHOT_API_KEY}'
        }
        
        payload = {
            'model': 'moonshot-v1-8k',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(MOONSHOT_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            return jsonify({'analysis': analysis})
        else:
            return jsonify({'error': 'AI分析服务暂时不可用'})
            
    except Exception as e:
        return jsonify({'error': f'AI分析失败: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
