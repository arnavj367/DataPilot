# DataPilot — Local AI Data Analyst

## Overview

DataPilot is a beginner-friendly, AI-powered CSV analysis application built with Python, Pandas, Streamlit, and Ollama. It allows users to upload tabular data and ask questions in natural language.

The application uses a locally running language model to interpret questions and select appropriate analysis tools. Pandas performs the numerical analysis, and the agent uses the tool results to formulate answers.

Model inference runs locally on your computer, so no hosted AI API key is required.

## Features

- Upload and analyze CSV datasets.
- Inspect dataset structure, columns, data types, and missing values.
- Calculate summary statistics.
- Group data and perform aggregations.
- Analyze correlations between numeric columns.
- Detect potential outliers using the interquartile range (IQR).
- Analyze trends using date-based aggregation.
- Save and retrieve persistent memories through the application's memory interface.
- Run the AI model locally using Ollama.

## Technology Stack

- **Python:** Application logic and integration.
- **Pandas:** Tabular data processing and numerical analysis.
- **Streamlit:** User interface.
- **Ollama:** Local language model execution.
- **Qwen 2.5 3B:** Local model used for agent reasoning and tool selection.
- **SQLite:** Persistent memory storage.
- **Matplotlib and Plotly:** Visualization libraries, where used by the application.

## Analysis Tools

DataPilot includes seven distinct analysis tools:

1. `inspect_dataset` — Inspects dataset dimensions, columns, data types, missing values, and a data preview.
2. `summary_statistics` — Calculates statistics such as count, mean, median, minimum, maximum, standard deviation, and sum.
3. `group_and_aggregate` — Groups data by a selected column and calculates supported aggregations such as sum, mean, median, minimum, maximum, or count.
4. `missing_value_analysis` — Identifies missing values in dataset columns.
5. `correlation_analysis` — Calculates Pearson correlation between two numeric columns.
6. `detect_outliers` — Identifies potential outliers using the IQR method.
7. `analyze_trend` — Aggregates date-based data at supported time intervals.

The agent can select an appropriate tool based on the user's question. Numerical answers should be grounded in the results returned by the analysis tools rather than generated from model knowledge alone.

## Persistent Memory

DataPilot includes a persistent memory component backed by SQLite.

Users can save, view, and delete memories through the application's memory interface. Saved memories can provide relevant context to the agent in later interactions, including after refreshing or reopening the application.

Memory is separate from the analysis tools: it provides contextual information, while Pandas-based tools perform the actual dataset calculations.

The SQLite memory database is generated locally and should not be committed to the public repository.

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- Git, or a downloaded ZIP of the repository
- Ollama for Windows
- Sufficient disk space for the selected language model

A computer with 8 GB RAM may run a small model such as `qwen2.5:3b`, although performance depends on available memory and hardware.

## Installation and Setup

### 1. Install Ollama and download the model

Install Ollama from:

https://ollama.com/download/windows

Open PowerShell and run:

```powershell
ollama --version
ollama pull qwen2.5:3b
ollama list
```

To test the model:

```powershell
ollama run qwen2.5:3b
```

Ask a short question and type `/bye` to exit.

Ollama normally provides its local API at `http://localhost:11434`.

### 2. Download the project

Clone the repository:

```powershell
git clone https://github.com/arnavj367/DataPilot.git
```

Replace `YOUR_PUBLIC_GITHUB_REPOSITORY_URL` with the actual URL of this repository.

Move into the project directory:

```powershell
cd DataPilot
```

If you downloaded a ZIP instead, extract it and open PowerShell in the extracted project folder.

### 3. Create a virtual environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, run this in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Alternatively, use `.venv\Scripts\python.exe` directly without activating the environment.

### 4. Test the analysis tools

```powershell
python test_tools.py
```

This smoke test checks the analysis tools and sample data without requiring an AI model call.

### 5. Test the agent

Ensure Ollama is running and the model has been downloaded:

```powershell
python test_agent.py
```

The sample sales dataset has these expected revenue totals by region:

- East: 60,000
- North: 93,000
- South: 125,000
- West: 75,000

Therefore, South should have the highest total revenue. The model's explanation may vary, but the numerical result should come from the analysis tool.

### 6. Launch the application

```powershell
python -m streamlit run app.py
```

Open the local URL displayed by Streamlit, usually:

http://localhost:8501

## Project Structure

```text
DataPilot/
├── app.py
├── agent.py
├── tools.py
├── memory.py
├── requirements.txt
├── test_agent.py
├── test_tools.py
├── README.md
└── data/
    └── sample_sales.csv
```

- `app.py` — Streamlit user interface.
- `agent.py` — AI agent and tool-selection logic.
- `tools.py` — Dataset analysis functions.
- `memory.py` — Persistent memory functionality.
- `requirements.txt` — Python dependencies.
- `test_tools.py` — Analysis-tool smoke tests.
- `test_agent.py` — Agent smoke test.
- `data/sample_sales.csv` — Example dataset.

## Troubleshooting

### `ollama` is not recognized

Close and reopen PowerShell after installing Ollama. If the issue persists, check the installation and Windows PATH.

### Cannot connect to Ollama

Open the Ollama application and confirm that it is running. Check available models with:

```powershell
ollama list
```

### Model not found

Download the required model:

```powershell
ollama pull qwen2.5:3b
```

Ensure that the model name configured in the application matches the downloaded model.

### Tool calls are not working correctly

Smaller language models may occasionally select or format tools incorrectly. Begin with simple questions, such as:

"Which region has the highest total Revenue?"

### Port 8501 is already in use

Start Streamlit on another port:

```powershell
python -m streamlit run app.py --server.port 8502
```

## Privacy and Cost

DataPilot uses an Ollama process running locally on the user's computer. With the local model configuration, the project does not require a third-party model API key or per-token API billing.

Prompts and dataset-derived tool results are sent to the local Ollama process for inference. Installing dependencies and downloading the model require internet access.

Users should avoid uploading confidential datasets or storing sensitive information in saved memories when using a public or shared computer.

## Limitations

- Analysis is limited to the operations supported by the available tools.
- Language-model tool selection and explanations may vary.
- Performance depends on the computer's hardware and the selected model.
- The application requires a compatible local Ollama installation and an available model.

## License

No license has been specified yet. Add an appropriate license if you want to grant the community explicit permissions to reuse, modify, or redistribute this project.
