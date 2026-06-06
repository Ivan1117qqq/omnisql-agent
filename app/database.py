import os
from sqlalchemy import create_engine, inspect, text

class DatabaseManager:
    def __init__(self):
        # 支援 PostgreSQL, MySQL 或 SQLite
        self.db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
        self.engine = create_engine(self.db_url)
        
    def get_schema_context(self) -> str:
        """動態提取資料庫結構（Schema），用於注入 Prompt"""
        inspector = inspect(self.engine)
        schema_text = []
        
        for table_name in inspector.get_table_names():
            schema_text.append(f"Table: {table_name}")
            columns = inspector.get_columns(table_name)
            col_details = []
            for col in columns:
                col_type = str(col['type'])
                is_nullable = "NULL" if col['nullable'] else "NOT NULL"
                col_details.append(f"  - {col['name']} ({col_type}) {is_nullable}")
            schema_text.append("\n".join(col_details))
            
            # 提取外鍵關係
            fk_relations = inspector.get_foreign_keys(table_name)
            for fk in fk_relations:
                schema_text.append(f"  - Foreign Key: {table_name}.{fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}")
            schema_text.append("-" * 30)
            
        return "\n".join(schema_text)

    def execute_query(self, sql_query: str):
        """在沙盒中執行 SQL，成功則回傳結果，失敗則拋出 Exception"""
        with self.engine.connect() as connection:
            result = connection.execute(text(sql_query))
            # 若為 SELECT 語句，回傳資料內容
            if result.returns_rows:
                return [dict(row._mapping) for row in result.fetchall()]
            return {"status": "success", "row_count": result.rowcount}