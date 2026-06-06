import os
from dotenv import load_dotenv
from app.database import DatabaseManager
from app.agent import OmniSQLAgent

load_dotenv()

def main():
    print("=== OmniSQL-Agent 啟動 ===")
    db = DatabaseManager()
    agent = OmniSQLAgent(db_manager=db)
    
    # 測試用互動環境
    while True:
        question = input("\n請輸入你的資料查詢問題 (或輸入 'exit' 離開): ")
        if question.lower() == 'exit':
            break
        if not question.strip():
            continue
            
        response = agent.generate_and_execute(question)
        print("\n=== 執行結果 ===")
        import json
        print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()