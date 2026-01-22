"""Booklist - 书单收集、标准化与对比工具"""
from fastapi import FastAPI
from app.database import init_db

app = FastAPI(
    title="Booklist",
    description="书单收集、标准化与对比工具",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    """启动时初始化数据库"""
    init_db()


@app.get("/")
def root():
    return {
        "name": "Booklist",
        "description": "书单收集、标准化与对比工具",
        "layers": {
            "1_raw_booklist": "原始书单 - 爬取的原始数据",
            "2_booklist": "书单层 - 按人物/来源汇总",
            "3_meta_booklist": "元书单 - 用户自定义合并，按频次排序",
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}
