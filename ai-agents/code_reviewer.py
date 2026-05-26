"""
AI Code Reviewer — Using LangChain + Ollama (CodeLlama)
Stage 8 of Jenkins Pipeline

What it does:
- Reads app/app.py
- Sends code to local CodeLlama model via LangChain
- Gets back security issues, bugs, suggestions
- Saves report to reports/ai_code_review.json
"""

import json
import os
import sys
import time

def review_code():
    try:
        from langchain_community.llms import Ollama
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
    except ImportError:
        print("Installing langchain...")
        os.system("pip install langchain langchain-community -q")
        from langchain_community.llms import Ollama
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain

    print("🤖 AI Code Reviewer Starting...")

    # Read source code
    code_path = "app/app.py"
    if not os.path.exists(code_path):
        print(f"❌ File not found: {code_path}")
        return

    with open(code_path, 'r') as f:
        code = f.read()

    # Connect to local Ollama
    try:
        llm = Ollama(
            model="codellama",
            base_url="http://localhost:11434",
            timeout=120
        )
    except Exception as e:
        print(f"⚠️ Ollama not available: {e}")
        print("📝 Saving placeholder report...")
        save_report({"status": "ollama_not_available", "message": str(e)})
        return

    # Create review prompt
    prompt = PromptTemplate(
        input_variables=["code"],
        template="""You are a senior security engineer reviewing Python code.

Analyze this code and provide:
1. Security vulnerabilities found
2. Bug risks
3. Code quality issues
4. Suggested fixes

Code:
{code}

Respond in JSON format:
{{
  "vulnerabilities": [],
  "bugs": [],
  "suggestions": [],
  "severity_score": "LOW/MEDIUM/HIGH",
  "summary": ""
}}"""
    )

    # Run review
    print(f"📝 Reviewing: {code_path}")
    start = time.time()

    try:
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(code=code)
        duration = time.time() - start

        report = {
            "file": code_path,
            "model": "codellama",
            "framework": "langchain",
            "duration_seconds": round(duration, 2),
            "review": result
        }

        save_report(report)
        print(f"✅ AI Code Review Complete ({duration:.1f}s)")
        print(f"📁 Report: reports/ai_code_review.json")

    except Exception as e:
        print(f"⚠️ Review error: {e}")
        save_report({"error": str(e), "file": code_path})


def save_report(data):
    os.makedirs("reports", exist_ok=True)
    with open("reports/ai_code_review.json", 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    review_code()
