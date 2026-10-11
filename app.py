"""Streamlit interface for the local DataPilot data-analysis agent."""
from pathlib import Path
import pandas as pd
import streamlit as st
from agent import ask_agent
from memory import save_memory, get_memories, delete_memory, clear_memories

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "data" / "sample_sales.csv"

st.set_page_config(page_title="DataPilot | Local AI Data Analyst", page_icon="📊", layout="wide")
st.title("📊 DataPilot")
st.caption("A local AI data analyst powered by Ollama + Pandas. Your data is processed on this computer.")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Ollama model", value="qwen2.5:3b", help="Use a model you have downloaded with Ollama.")
    st.markdown("**First time?** In PowerShell run `ollama pull qwen2.5:3b`.")
    st.divider()
    st.write("Try questions like:")
    st.write("- Which region has the highest total revenue?")
    st.write("- Summarize the Revenue column.")
    st.write("- Are there missing values?")
    st.write("- Find outliers in Profit.")
    
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
    df = pd.read_csv(DEFAULT_CSV)
    dataset_name = "sample_sales.csv"
    st.info("Using the included sample dataset. Upload your own CSV to analyze another dataset.")

st.subheader(f"Dataset: {dataset_name}")
m1, m2, m3 = st.columns(3)
m1.metric("Rows", f"{len(df):,}")
m2.metric("Columns", f"{len(df.columns):,}")
m3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")

with st.expander("Preview dataset", expanded=True):
    st.dataframe(df.head(100), use_container_width=True)
    st.caption("Column names: " + ", ".join(map(str, df.columns)))

st.divider()
st.header("📈 Interactive Charts")

# Identify columns suitable for plotting.
numeric_columns = df.select_dtypes(include="number").columns.tolist()
all_columns = df.columns.tolist()

if len(all_columns) >= 1 and len(numeric_columns) >= 1:
    chart_type = st.selectbox(
        "Choose chart type",
        [
            "Bar chart",
            "Line chart",
            "Scatter plot",
            "Histogram",
            "Box plot",
        ],
    )

    if chart_type == "Histogram":
        value_column = st.selectbox(
            "Choose a numeric column",
            numeric_columns,
            key="histogram_column",
        )

        import plotly.express as px

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

        import plotly.express as px

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
            col for col in numeric_columns
            if col != x_column
        ]

        if x_column in numeric_columns:
            y_options = numeric_columns

        if y_options:
            y_column = st.selectbox(
                "Choose the Y-axis",
                y_options,
                key="chart_y_column",
            )

            import plotly.express as px

            if chart_type == "Bar chart":
                # Aggregate repeated categories so the chart is easier to read.
                if not pd.api.types.is_numeric_dtype(df[x_column]):
                    plot_df = (
                        df.groupby(x_column, dropna=False)[y_column]
                        .sum()
                        .reset_index()
                    )
                    fig = px.bar(
                        plot_df,
                        x=x_column,
                        y=y_column,
                        title=f"{y_column} by {x_column}",
                        template="plotly_white",
                    )
                else:
                    fig = px.bar(
                        df,
                        x=x_column,
                        y=y_column,
                        title=f"{y_column} by {x_column}",
                        template="plotly_white",
                    )

            elif chart_type == "Line chart":
                plot_df = df.copy()

                # Try to order date-like X-axis values chronologically.
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

            else:  # Scatter plot
                fig = px.scatter(
                    df,
                    x=x_column,
                    y=y_column,
                    title=f"{y_column} vs {x_column}",
                    template="plotly_white",
                )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Choose an X-axis that leaves a numeric column available for the Y-axis.")

else:
    st.info("Upload a dataset containing at least one numeric column to create charts.")


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
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing locally with Ollama..."):
            try:
                answer, trace = ask_agent(df, question, model=model.strip() or "qwen2.5:3b")
                st.markdown(answer)
                if trace:
                    with st.expander("Analysis steps / tool trace"):
                        st.json(trace)
                st.session_state.chat_history.append({
                    "role": "assistant", "content": answer, "trace": trace
                })
            except Exception as exc:
                message = (
                    "I couldn't connect to Ollama. Check that Ollama is installed and running, "
                    f"and that model `{model}` is downloaded. Details: `{exc}`"
                )
                st.error(message)
                st.session_state.chat_history.append({
                    "role": "assistant", "content": message, "trace": []
                })

if st.button("Clear chat history"):
    st.session_state.chat_history = []
    st.rerun()
