# DataPilot — Local AI Data Analyst

DataPilot is a beginner-friendly CSV analysis app built with Python, Pandas, Streamlit, and Ollama. Model inference runs locally on your computer; no hosted AI API key is required.

## Requirements

- Windows 10/11
- Python 3.10 or newer (Python 3.11 is a good choice)
- Ollama for Windows
- Enough disk space to download a model
- 8 GB RAM can run a small model such as `qwen2.5:3b`; performance depends on hardware and GPU VRAM.

## 1. Install Ollama and download the model

Install Ollama from https://ollama.com/download/windows, then open a new PowerShell terminal:

```powershell
ollama --version
ollama pull qwen2.5:3b
ollama list
```

Ollama normally runs as a background service on `http://localhost:11434`.

Test the model:

```powershell
ollama run qwen2.5:3b
```

Ask it a short question, then type `/bye`.

## 2. Open this project in PowerShell

Extract the ZIP to a folder you can find easily. For example:

```powershell
cd "$HOME\Documents\DataPilot_Ollama"
```

Use the actual extracted folder path if different.

## 3. Create and activate a virtual environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can run this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Or skip activation and use `.venv\Scripts\python.exe` explicitly.

## 4. Test the Pandas tools first

```powershell
python test_tools.py
```

This test does not call the AI model. It verifies the analysis functions and sample data.

## 5. Test the local AI agent

Make sure Ollama is running and the model is downloaded, then:

```powershell
python test_agent.py
```

The sample dataset has these revenue totals by region:
- East: 60,000
- North: 93,000
- South: 125,000
- West: 75,000

So South is expected to have the highest total revenue. The model's explanation can vary, but the numeric result should come from the Pandas tool.

## 6. Launch the Streamlit app

```powershell
python -m streamlit run app.py
```

Streamlit prints a local URL, usually http://localhost:8501. Open that address in your browser.

## Available tools

- `inspect_dataset`: dataset size, columns, data types, missing counts, preview
- `summary_statistics`: count, mean, median, min, max, standard deviation, sum
- `group_and_aggregate`: group by a category and calculate sum/mean/median/min/max/count
- `missing_value_analysis`: missing cells by column
- `correlation_analysis`: Pearson correlation between two numeric columns
- `detect_outliers`: IQR outlier detection
- `analyze_trend`: daily, weekly, monthly, or quarterly time aggregation

## Troubleshooting

### `ollama` is not recognized
Close and reopen PowerShell after installing Ollama. If still not found, restart Windows and check the installation.

### Connection refused / cannot connect
Open the Ollama app and check that it is running. In PowerShell run `ollama list`. The local API should be available at `http://localhost:11434`.

### Model not found
Run `ollama pull qwen2.5:3b`, then check `ollama list`. The model name in the app must match a downloaded model exactly.

### Tool calls are not happening
Small models sometimes fail to select or format tools correctly. First test with simple questions such as “Which region has the highest total Revenue?” Try a newer tool-capable model only if your hardware can handle it.

### Port 8501 is already in use
Run `python -m streamlit run app.py --server.port 8502`.

## Privacy and cost

DataPilot sends prompts and dataset-derived tool results to the Ollama process running locally. With the local model, this project does not require a third-party model API key or per-token API billing. Installing/downloading Ollama and model files requires internet access.
