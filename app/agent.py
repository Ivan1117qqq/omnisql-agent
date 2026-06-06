import os
import re
from openai import OpenAI
from app.database import DatabaseManager

class OmniSQLAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        # 支援 OpenAI 或任何自建的 OpenAI-compatible API (如 Ollama, vLLM)
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "mock-key"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        self.model = os.getenv("LLM_MODEL", "gpt-4o")
        self.max_retries = 3

    def _clean_sql(self, llm_output: str) -> str:
        """清洗 Markdown 標記，只留下純 SQL"""
        sql_match = re.search(r"```sql\n(.*?)\n```", llm_output, re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        return llm_output.strip()

    def generate_and_execute(self, user_question: str) -> dict:
        schema_context = self.db.get_schema_context()
        
        # 初始 System Prompt 建立
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert data analyst. Your job is to convert natural language questions into executable SQL queries.\n"
                    f"Here is the database schema:\n{schema_context}\n"
                    "Respond ONLY with the SQL query wrapped in a ```sql ... ``` block. Do not write any explanations."
                )
            },
            {"role": "user", "content": f"Question: {user_question}"}
        ]

        attempt = 0
        last_failed_sql = ""

        while attempt < self.max_retries:
            print(f"[*] 正在嘗試生成/修正 SQL... (第 {attempt + 1} 次嘗試)")
            
            # 呼叫 LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0  # 精確任務將 Temperature 設為 0
            )
            
            raw_output = response.choices[0].message.content
            sql_query = self._clean_sql(raw_output)
            print(f"[->] 生成的 SQL:\n{sql_query}")

            try:
                # 進入沙盒測試執行
                query_result = self.db.execute_query(sql_query)
                print("[+] SQL 執行成功！")
                return {
                    "success": True,
                    "sql": sql_query,
                    "result": query_result,
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                # 關鍵：Self-Correction 邏輯
                error_message = str(e)
                print(f"[!] 執行失敗。錯誤訊息: {error_message}")
                
                # 將錯誤訊息與失敗的 SQL 作為上下文反饋給 LLM
                messages.append({"role": "assistant", "content": raw_output})
                messages.append({
                    "role": "user",
                    "content": (
                        f"The previous SQL query failed with the following error:\n{error_message}\n"
                        "Please analyze the error, fix the column/table names or syntax, and provide a corrected SQL query."
                    )
                })
                attempt += 1
                
        return {
            "success": False,
            "error": "Max retries reached. Could not generate valid SQL.",
            "last_sql": sql_query
        }