
"""Streamlit interface for DataPilot: local Ollama or cloud Gemini."""
from pathlib import Path

import pandas as pd
import streamlit as st
from agent import ask_agent
from memory import save_memory, get_memories, delete_memory, clear_memories

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "data" / "sample_sales.csv"

st.set_page_config(
    page_title="DataPilot | AI Data Analyst",
    page_icon="📊",
    layout="wide",
)

st.title("📊 DataPilot")
st.caption(
    "An AI data analyst powered by Pandas tools. "
    "Choose local Ollama or cloud Gemini below."
)

with st.sidebar:
    st.header("Settings")

    provider = st.radio(
        "AI backend",
        options=["Ollama (local)", "Gemini (cloud)"],
        index=0,
        help="Ollama runs on your computer. Gemini uses an online API.",
    )

    if provider == "Ollama (local)":
        model = st.text_input(
            "Ollama model",
            value="qwen2.5:3b",
            help="Use a model downloaded with Ollama.",
        )
        st.caption("First time? Run `ollama pull qwen2.5:3b` in PowerShell.")
        selected_provider = "ollama"
        selected_model = model.strip() or "qwen2.5:3b"
    else:
        selected_provider = "gemini"
        selected_model = "gemini-3.5-flash-lite"
        st.caption(f"Gemini model: `{selected_model}`")
        st.caption("The API key is read from Streamlit Secrets.")
    
    st.divider()
    st.header("🧠 Persistent Memory")
    st.caption("Save information locally for future sessions.")

    memory_text = st.text_area(
        "Information to remember",
        placeholder="Example: I prefer charts with clear labels.",
        key="memory_text_input",
    )

    memory_category = st.selectbox(
        "Memory category",
        ["Preference", "Project", "Instruction", "General"],
        key="memory_category_input",
    )

    if st.button("💾 Save Memory", key="save_memory_button"):
        if memory_text.strip():
            save_memory(memory_text, memory_category.lower())
            st.success("Memory saved!")
            st.rerun()
        else:
            st.warning("Enter some information first.")

    st.subheader("Saved Memories")
    saved_memories = get_memories()

    if saved_memories:
        for item in saved_memories:
            st.write(f"#{item['id']} · {item['category'].title()}")
            st.write(item["content"])

            if st.button(
                f"Delete memory #{item['id']}",
                key=f"delete_memory_{item['id']}",
            ):
                delete_memory(item["id"])
                st.rerun()

        if st.button("🗑️ Clear All Memories", key="clear_all_memories"):
            clear_memories()
            st.rerun()
    else:
        st.info("No saved memories yet.")
uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        dataset_name = uploaded.name
    except Exception as exc:
        st.error(f"Could not read this CSV: {exc}")
        st.stop()
else:
    try:
        df = pd.read_csv(DEFAULT_CSV)
        dataset_name = "sample_sales.csv"
        st.info(
            "Using the included sample dataset. "
            "Upload your own CSV to analyze another dataset."
        )
    except Exception as exc:
        st.error(f"Could not load the sample dataset: {exc}")
        st.stop()

st.subheader(f"Dataset: {dataset_name}")

m1, m2, m3 = st.columns(3)
m1.metric("Rows", f"{len(df):,}")
m2.metric("Columns", f"{len(df.columns):,}")
m3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")

with st.expander("Preview dataset", expanded=True):
    st.dataframe(df.head(100), use_container_width=True)
    st.caption("Column names: " + ", ".join(map(str, df.columns)))

st.divider()
st.header("📊 Interactive Charts")

numeric_columns = df.select_dtypes(include="number").columns.tolist()
all_columns = df.columns.tolist()

if all_columns and numeric_columns:
    chart_type = st.selectbox(
        "Choose chart type",
        ["Bar chart", "Line chart", "Scatter plot", "Histogram", "Box plot"],
    )

    import plotly.express as px

    if chart_type == "Histogram":
        value_column = st.selectbox(
            "Choose a numeric column",
            numeric_columns,
            key="histogram_column",
        )
        fig = px.histogram(
            df,
            x=value_column,
            title=f"Distribution of {value_column}",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Box plot":
        value_column = st.selectbox(
            "Choose a numeric column",
            numeric_columns,
            key="box_column",
        )
        fig = px.box(
            df,
            y=value_column,
            title=f"Box Plot of {value_column}",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        x_column = st.selectbox(
            "Choose the X-axis",
            all_columns,
            key="chart_x_column",
        )

        y_options = [
            col for col in numeric_columns if col != x_column
        ]

        if x_column in numeric_columns:
            y_options = numeric_columns

        if y_options:
            y_column = st.selectbox(
                "Choose the Y-axis",
                y_options,
                key="chart_y_column",
            )

            if chart_type == "Bar chart":
                if not pd.api.types.is_numeric_dtype(df[x_column]):
                    plot_df = (
                        df.groupby(x_column, dropna=False)[y_column]
                        .sum()
                        .reset_index()
                    )
                else:
                    plot_df = df

                fig = px.bar(
                    plot_df,
                    x=x_column,
                    y=y_column,
                    title=f"{y_column} by {x_column}",
                    template="plotly_white",
                )

            elif chart_type == "Line chart":
                plot_df = df.copy()

                if not pd.api.types.is_numeric_dtype(plot_df[x_column]):
                    parsed_dates = pd.to_datetime(
                        plot_df[x_column], errors="coerce"
                    )
                    if parsed_dates.notna().all():
                        plot_df[x_column] = parsed_dates
                        plot_df = plot_df.sort_values(x_column)

                fig = px.line(
                    plot_df,
                    x=x_column,
                    y=y_column,
                    markers=True,
                    title=f"{y_column} over {x_column}",
                    template="plotly_white",
                )

            else:
                fig = px.scatter(
                    df,
                    x=x_column,
                    y=y_column,
                    title=f"{y_column} vs {x_column}",
                    template="plotly_white",
                )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning(
                "Choose an X-axis that leaves a numeric column "
                "available for the Y-axis."
            )
else:
    st.info(
        "Upload a dataset containing at least one numeric column "
        "to create charts."
    )


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for item in st.session_state.chat_history:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item.get("trace"):
            with st.expander("Analysis steps / tool trace"):
                st.json(item["trace"])

question = st.chat_input("Ask a question about your data...")

if question:
    st.session_state.chat_history.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            if selected_provider == "gemini":
                api_key = st.secrets.get("GEMINI_API_KEY", "")
                if not api_key:
                    st.error(
                        "Gemini API key not configured. Add GEMINI_API_KEY "
                        "in the app's Streamlit Secrets settings."
                    )
                    st.stop()

                spinner_text = "Analyzing with Gemini..."
            else:
                api_key = None
                spinner_text = "Analyzing locally with Ollama..."

            with st.spinner(spinner_text):
                answer, trace = ask_agent(
                    df,
                    question,
                    model=selected_model,
                    provider=selected_provider,
                    api_key=api_key,
                )

            st.markdown(answer)
            if trace:
                with st.expander("Analysis steps / tool trace"):
                    st.json(trace)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "trace": trace,
            })

        except Exception as exc:
            if selected_provider == "gemini":
                message = (
                    "Gemini could not complete the request. Check your API key, "
                    "model availability, network access, and tool-call errors. "
                    f"Details: {exc}"
                )
            else:
                message = (
                    "I couldn't connect to Ollama. Check that Ollama is installed "
                    f"and running and that `{selected_model}` is downloaded. "
                    f"Details: {exc}"
                )

            st.error(message)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": message,
                "trace": [],
            })

if st.button("Clear chat history"):
    st.session_state.chat_history = []
    st.rerun()
