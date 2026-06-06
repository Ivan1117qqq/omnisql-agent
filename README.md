# OmniSQL-Agent 🚀

An enterprise-grade Text-to-SQL autonomous Agent featuring dynamic schema distillation and runtime self-correction feedback loops.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🌟 Overview

**OmniSQL-Agent** bridges the gap between natural language and complex relational databases. Unlike naive text-to-SQL implementations that fail on massive enterprise schemas or invalid syntax, OmniSQL-Agent introduces a **Self-Correction Runtime Loop** that cross-compiles, executes, and heals SQL queries in a sandboxed environment before returning results.

### 🔑 Key Features

- **Runtime Self-Correction:** Automatically intercepts database exceptions, pipes the error log back to the LLM, and regenerates queries dynamically (up to $N$ retries).
- **Dynamic Schema Context:** Inspects database catalogs on-the-fly, mapping tables, column types, and Foreign Key relations into structured context prompts.
- **LLM Agnostic:** Seamlessly integrates with OpenAI (GPT-4o), Ollama, vLLM, or any OpenAI-compatible API gateway.
- **Production Ready:** Out-of-the-box containerization with Docker and Docker Compose, including an isolated PostgreSQL sandbox.

---

## 🏗️ Architecture Flow

```text
User Question ──> [OmniSQLAgent] ──> Inject Live Schema Context
                         │
                         ▼
             ┌──> [LLM Generation]
             │           │
             │           ▼
     Error Feedback  [Sandbox Execution] ──(Fails)──┐
             │           │                          │
             │        (Passes)                      ▼
             │           │                 Parse DB Error Log
             └───────────┴──────────────────────────┘
                         │
                         ▼
                Valid Result Returned
```