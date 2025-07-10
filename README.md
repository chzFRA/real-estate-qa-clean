# 🏗️ Real Estate Legal QA System

This repository contains the full pipeline and codebase for an automated **Legal Question-Answering system** tailored to **New Zealand real estate laws**. It supports extracting structured content from law PDFs, cleaning, and generating QA pairs using large language models.

---

## 📁 Project Structure


---

## ⚙️ How to Run

1. **Download legal PDFs**
    ```bash
    python download_pdf.py
    ```

2. **Extract and clean text**
    ```bash
    python extract_text.py
    python smart_cleaner.py
    ```

3. **Generate Q&A pairs**
    ```bash
    python generate_qa.py
    ```

4. **Run the full pipeline**
    ```bash
    python run_pipeline.py
    ```

---

## 📦 Dependencies

Install all dependencies using:

```bash
pip install -r requirements.txt

All secrets (e.g., OpenAI, Anthropic keys) should be stored in a .env file like:

OPENAI_API_KEY=sk-xxxxxxxxxx
ANTHROPIC_API_KEY=claude-xxxxxxxxx