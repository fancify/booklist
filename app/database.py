"""数据库配置"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# 数据库文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR}/booklist.db"

# 创建引擎
engine = create_engine(DATABASE_URL, echo=False)

# Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库session（用于FastAPI依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    from app.models import Base
    Base.metadata.create_all(bind=engine)
