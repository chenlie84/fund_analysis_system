# 基金智能分析系统部署指南

## 🚀 部署方式概览

基金智能分析系统支持多种部署方式，包括本地部署、Vercel Serverless部署、Docker容器部署等。

## 📦 部署选项

### 1. Vercel部署（推荐）

#### 前置要求
- GitHub账户
- Vercel账户（免费注册）

#### 部署步骤

1. **准备代码**
   ```bash
   # 确保项目结构完整
   fund_analysis_system/
   ├── vercel_app.py          # Vercel入口文件
   ├── realtime_fund_analyzer.py
   ├── templates/
   │   └── index.html
   ├── requirements.txt
   ├── vercel.json
   └── ...
   ```

2. **GitHub仓库**
   ```bash
   cd fund_analysis_system
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/fund-analysis-system.git
   git push -u origin main
   ```

3. **Vercel部署**
   - 访问 [vercel.com](https://vercel.com)
   - 点击 "New Project"
   - 导入GitHub仓库
   - 保持默认配置，点击 "Deploy"

4. **环境变量配置**（可选）
   - 在Vercel控制台 → Settings → Environment Variables
   - 添加 `MOONSHOT_API_KEY`（用于AI分析功能）

#### 访问地址
部署完成后，Vercel会提供类似 `https://fund-analysis-system.vercel.app` 的域名

### 2. 本地部署

#### 环境要求
- Python 3.9+
- pip包管理器

#### 安装步骤
```bash
# 克隆项目
git clone <your-repo-url>
cd fund_analysis_system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python fund_web_app.py
```

#### 访问地址
- 本地: http://localhost:8080
- 网络: http://[你的IP]:8080

### 3. Docker部署

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "fund_web_app:app", "-w", "4", "-b", "0.0.0.0:8080"]
```

#### 构建和运行
```bash
# 构建镜像
docker build -t fund-analysis-system .

# 运行容器
docker run -p 8080:8080 fund-analysis-system
```

### 4. 云服务器部署

#### 使用Gunicorn
```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn fund_web_app:app -w 4 -b 0.0.0.0:8080
```

#### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔧 环境配置

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `MOONSHOT_API_KEY` | Moonshot AI API密钥（可选） | `sk-xxx...` |
| `FLASK_ENV` | 运行环境 | `production` |
| `PORT` | 端口号 | `8080` |

### 配置文件示例

#### `.env` 文件（本地开发）
```bash
MOONSHOT_API_KEY=your-moonshot-api-key
FLASK_ENV=development
PORT=8080
```

#### Vercel环境变量
在Vercel控制台设置：
- `MOONSHOT_API_KEY`: 你的Moonshot API密钥

## 📊 部署验证

### 健康检查
```bash
# 测试API接口
curl https://your-domain.vercel.app/api/search_funds?keyword=沪深300&limit=3

# 测试页面
curl https://your-domain.vercel.app/
```

### 功能测试清单
- [ ] 基金搜索功能
- [ ] 基金详情展示
- [ ] 净值图表显示
- [ ] 定投回测计算
- [ ] AI分析功能（如配置了API Key）

## 🚨 常见问题

### 1. Vercel部署失败
**问题**: 构建失败或超时
**解决**:
- 检查 `requirements.txt` 中的包版本
- 确保 `vercel.json` 配置正确
- 查看Vercel构建日志

### 2. 数据获取失败
**问题**: akshare接口超时
**解决**:
- 检查网络连接
- 增加超时时间
- 考虑使用代理

### 3. 内存不足
**问题**: Vercel Serverless内存限制
**解决**:
- 优化数据处理逻辑
- 减少单次请求的数据量
- 使用缓存策略

### 4. 跨域问题
**问题**: 前端API调用失败
**解决**:
- Flask已自动处理CORS
- 检查API端点URL是否正确

## 🎯 性能优化

### Vercel优化
- 使用CDN加速静态资源
- 启用压缩传输
- 合理设置缓存头

### 代码优化
- 减少不必要的依赖
- 优化数据处理逻辑
- 使用连接池

## 📈 监控和日志

### Vercel Analytics
- 访问Vercel控制台查看实时分析
- 监控API响应时间
- 查看错误日志

### 自定义监控
```python
# 添加日志记录
import logging
logging.basicConfig(level=logging.INFO)
```

## 🔒 安全建议

### 生产环境
- 使用HTTPS
- 配置防火墙
- 定期更新依赖
- 限制API访问频率

### 敏感信息
- 不要将API密钥提交到代码仓库
- 使用环境变量存储敏感信息
- 定期轮换密钥

## 📞 技术支持

### 部署问题
- GitHub Issues: [项目仓库](https://github.com/yourusername/fund-analysis-system/issues)
- 邮件支持: your-email@example.com

### 社区资源
- Vercel文档: [vercel.com/docs](https://vercel.com/docs)
- Flask文档: [flask.palletsprojects.com](https://flask.palletsprojects.com)

---

**部署完成！** 🎉

选择最适合你的部署方式，开始享受专业的基金分析服务吧！
