# 基金智能分析系统 API 文档

## 📋 接口概览

所有API接口均采用RESTful设计，返回JSON格式数据。基础URL为：`http://localhost:8080/api`

## 🔍 基金搜索接口

### 搜索基金
**端点**: `GET /api/search_funds`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keyword | string | 是 | 搜索关键词（基金代码或名称） |
| limit | integer | 否 | 返回结果数量，默认10 |

**请求示例**:
```
GET /api/search_funds?keyword=沪深300&limit=5
```

**响应示例**:
```json
[
  {
    "基金代码": "000051",
    "基金简称": "华夏沪深300ETF联接A",
    "基金类型": "指数型"
  },
  {
    "基金代码": "110020",
    "基金简称": "易方达沪深300ETF联接A",
    "基金类型": "指数型"
  }
]
```

## 📊 基金详情接口

### 获取基金基本信息
**端点**: `GET /api/fund_info/{fund_code}`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fund_code | string | 是 | 基金代码 |

**请求示例**:
```
GET /api/fund_info/000051
```

**响应示例**:
```json
{
  "fund_code": "000051",
  "fund_name": "华夏沪深300ETF联接A",
  "fund_type": "指数型",
  "latest_nav": 1.2345,
  "daily_change": 0.56,
  "nav_date": "2025-07-18"
}
```

## 📈 历史数据接口

### 获取基金历史净值
**端点**: `GET /api/fund_history/{fund_code}`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fund_code | string | 是 | 基金代码 |
| start_date | string | 否 | 开始日期 (YYYYMMDD格式) |
| end_date | string | 否 | 结束日期 (YYYYMMDD格式) |

**请求示例**:
```
GET /api/fund_history/000051?start_date=20240101&end_date=20250718
```

**响应示例**:
```json
[
  {
    "净值日期": "2025-07-18",
    "单位净值": 1.2345,
    "累计净值": 2.3456
  },
  {
    "净值日期": "2025-07-17",
    "单位净值": 1.2289,
    "累计净值": 2.3400
  }
]
```

## 📊 基金表现接口

### 获取基金表现指标
**端点**: `GET /api/fund_performance/{fund_code}`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fund_code | string | 是 | 基金代码 |
| period | string | 否 | 时间周期 (1y, 3y, 5y)，默认1y |

**请求示例**:
```
GET /api/fund_performance/000051?period=1y
```

**响应示例**:
```json
{
  "fund_code": "000051",
  "total_return": 0.1234,
  "annual_return": 0.1234,
  "max_drawdown": -0.089,
  "volatility": 0.1567,
  "sharpe_ratio": 0.789
}
```

## 💰 定投回测接口

### 计算定投回测
**端点**: `POST /api/dca_backtest`

**请求体**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fund_code | string | 是 | 基金代码 |
| start_date | string | 是 | 开始日期 (YYYY-MM-DD格式) |
| end_date | string | 是 | 结束日期 (YYYY-MM-DD格式) |
| investment_amount | number | 是 | 每期投资金额 |
| frequency | string | 是 | 投资频率 (daily/weekly/monthly) |

**请求示例**:
```json
POST /api/dca_backtest
{
  "fund_code": "000051",
  "start_date": "2024-01-01",
  "end_date": "2025-07-18",
  "investment_amount": 1000,
  "frequency": "weekly"
}
```

**响应示例**:
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "nav": 1.1000,
      "shares": 909.09,
      "total_investment": 1000,
      "current_value": 1000,
      "total_return": 0
    }
  ],
  "summary": {
    "total_investment": 78000,
    "current_value": 85600,
    "total_return": 0.0974,
    "total_profit": 7600
  }
}
```

## 🤖 AI智能分析接口

### 获取AI投资建议
**端点**: `POST /api/ai_analysis`

**请求体**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fund_info | object | 是 | 基金基本信息 |
| dca_result | object | 是 | 回测结果数据 |
| performance | object | 是 | 基金表现指标 |

**请求示例**:
```json
POST /api/ai_analysis
{
  "fund_info": {
    "fund_code": "000051",
    "fund_name": "华夏沪深300ETF联接A",
    "fund_type": "指数型"
  },
  "dca_result": {
    "total_investment": 78000,
    "current_value": 85600,
    "total_return": 0.0974,
    "total_profit": 7600
  },
  "performance": {
    "total_return": 0.1234,
    "annual_return": 0.1234,
    "max_drawdown": -0.089,
    "volatility": 0.1567
  }
}
```

**响应示例**:
```json
{
  "analysis": "## 基金定投策略分析\n\n### 综合评价\n华夏沪深300ETF联接A作为宽基指数基金，在过去1.5年的定投回测中表现良好...\n\n### 风险提示\n1. 最大回撤达到8.9%，需要有一定风险承受能力...\n\n### 投资建议\n- 适合长期定投，建议持有3年以上...\n- 当前估值处于合理区间...\n\n### 适合投资者\n- 风险承受能力中等以上的投资者...\n- 追求稳健增长的长期投资者..."
}
```

## 📊 图表数据接口

### 获取图表数据
**端点**: `GET /api/chart_data/{fund_code}`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fund_code | string | 是 | 基金代码 |
| start_date | string | 否 | 开始日期 (YYYYMMDD格式) |
| end_date | string | 否 | 结束日期 (YYYYMMDD格式) |

**请求示例**:
```
GET /api/chart_data/000051
```

**响应示例**:
```json
{
  "chart": "{\"data\":[{\"x\":[\"2024-01-01\",\"2024-01-02\"],\"y\":[1.1,1.12],\"type\":\"scatter\",\"name\":\"单位净值\"}],\"layout\":{\"title\":\"基金净值走势\",\"xaxis\":{\"title\":\"日期\"},\"yaxis\":{\"title\":\"单位净值\"}}}"
}
```

## 🚨 错误处理

### 标准错误格式
所有API错误都遵循统一格式：

```json
{
  "error": "错误描述信息"
}
```

### 常见错误码

| HTTP状态码 | 错误描述 | 说明 |
|------------|----------|------|
| 400 | 参数错误 | 请求参数格式不正确 |
| 404 | 基金不存在 | 指定的基金代码不存在 |
| 500 | 服务器错误 | 内部处理错误 |
| 503 | 服务不可用 | 数据源服务异常 |

### 错误示例
```json
{
  "error": "无法获取基金数据或计算失败"
}
```

## 🔍 使用示例

### Python调用示例
```python
import requests

# 搜索基金
response = requests.get('http://localhost:8080/api/search_funds', 
                       params={'keyword': '沪深300', 'limit': 5})
funds = response.json()

# 获取基金详情
fund_code = '000051'
info = requests.get(f'http://localhost:8080/api/fund_info/{fund_code}').json()

# 定投回测
backtest_data = {
    "fund_code": "000051",
    "start_date": "2024-01-01",
    "end_date": "2025-07-18",
    "investment_amount": 1000,
    "frequency": "weekly"
}
result = requests.post('http://localhost:8080/api/dca_backtest', 
                      json=backtest_data).json()
```

### JavaScript调用示例
```javascript
// 搜索基金
fetch('/api/search_funds?keyword=沪深300&limit=5')
  .then(res => res.json())
  .then(data => console.log(data));

// 定投回测
fetch('/api/dca_backtest', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    fund_code: '000051',
    start_date: '2024-01-01',
    end_date: '2025-07-18',
    investment_amount: 1000,
    frequency: 'weekly'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

## 📋 接口限制

### 频率限制
- 搜索接口: 每分钟100次
- 详情接口: 每分钟200次
- 回测接口: 每分钟50次

### 数据范围
- 历史数据: 最多支持5年历史数据
- 回测时间: 最少3个月，最多5年
- 投资金额: 100-1000000元

## 🔧 测试工具

### curl测试
```bash
# 搜索基金
curl "http://localhost:8080/api/search_funds?keyword=沪深300&limit=3"

# 获取基金详情
curl "http://localhost:8080/api/fund_info/000051"

# 定投回测
curl -X POST http://localhost:8080/api/dca_backtest \
  -H "Content-Type: application/json" \
  -d '{"fund_code":"000051","start_date":"2024-01-01","end_date":"2025-07-18","investment_amount":1000,"frequency":"weekly"}'
```

---

**文档版本**: v1.0.0  
**最后更新**: 2025-07-18
