# Booklist

书单收集、标准化与对比工具。

## 功能

- 从豆瓣等平台爬取书单
- 数据标准化和去重
- 支持多书单合并和频次排序

## 项目结构

- `app/` - FastAPI 应用
- `scripts/` - 工具脚本
- `data/` - 数据库文件

## 本地开发

```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动FastAPI服务器
uvicorn app.main:app --reload
```

API文档访问 http://localhost:8000/docs

## 技术栈

- FastAPI
- SQLAlchemy
- BeautifulSoup
- Python
