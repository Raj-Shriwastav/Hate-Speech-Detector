import streamlit as st
import pandas as pd
import plotly.express as px
from comment_analyzer import CommentAnalyzer
import os
from dotenv import load_dotenv

# Initialize session state variables
if 'all_results_df' not in st.session_state:
    st.session_state.all_results_df = pd.DataFrame()
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0 # To reset file uploader
if 'current_file_name' not in st.session_state:
    st.session_state.current_file_name = None
if 'processing_started' not in st.session_state:
    st.session_state.processing_started = False

def main():
    load_dotenv()

    if not os.getenv('GROQ_API_KEY'):
        st.error("Please set your GROQ_API_KEY in the .env file")
        st.stop()

    try:
        analyzer = CommentAnalyzer()
    except ValueError as e:
        st.error(f"Initialization Error: {e}")
        st.stop()

    st.set_page_config(
        page_title="Comment Moderation System (Groq/Gemma 2)",
        page_icon="⚡",
        layout="wide"
    )

    st.title("⚡ Comment Moderation System (Groq/Gemma 2)")
    st.markdown("""
    Analyzes comments for toxicity using Groq Cloud's Gemma 2 model.
    Processes comments **sequentially**, ensuring a minimum **3-second interval** between API calls.
    Upload your file (CSV or JSON) and click 'Start Processing'.
    """)

    uploaded_file = st.file_uploader(
        "Upload your comments file (CSV or JSON)",
        type=['csv', 'json'],
        key=f"file_uploader_{st.session_state.file_uploader_key}"
    )

    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.current_file_name:

            st.session_state.current_file_name = uploaded_file.name
            st.info(f"New file uploaded: {uploaded_file.name}. Ready to process.")
            st.rerun()

        if not st.session_state.processing_started:
            if st.button("Start Processing All Comments"):
                st.session_state.processing_started = True
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df_upload = pd.read_csv(uploaded_file)
                    else:
                        df_upload = pd.read_json(uploaded_file)

                    if 'comment_text' not in df_upload.columns:
                        st.error("The uploaded file must contain a 'comment_text' column.")
                        st.session_state.processing_started = False
                        return

                    comments_to_process = df_upload['comment_text'].astype(str).dropna().tolist()
                    if not comments_to_process:
                        st.warning("No valid comments found in the 'comment_text' column.")
                        st.session_state.processing_started = False
                        return

                    total_comments = len(comments_to_process)
                    st.info(f"Starting analysis for {total_comments} comments...")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text("Processing comments...")

                    results_df = analyzer.process_comments(comments_to_process, progress_bar)

                    st.session_state.all_results_df = results_df.copy()

                    progress_bar.progress(1.0)
                    status_text.text(f"Processed {len(results_df)} comments.")
                    st.success(f"Analysis complete for {len(results_df)} comments!")
                    st.rerun()

                except Exception as e:
                    st.error(f"An error occurred during processing: {str(e)}")
                    st.session_state.processing_started = True # Keep marked as started (or attempted)

        if not st.session_state.all_results_df.empty:
            st.header("Analysis Results")
            current_results_df = st.session_state.all_results_df

            st.subheader("Summary Statistics")
            stats = analyzer.get_summary_stats(current_results_df)
            if stats:
                 col1, col2, col3 = st.columns(3)
                 col1.metric("Total Processed", stats.get('total_comments', 0))
                 col2.metric("Toxic Comments", stats.get('toxic_comments', 0))
                 avg_tox = stats.get('avg_toxicity', 0.0)
                 col3.metric("Average Toxicity", f"{avg_tox:.2f}" if avg_tox is not None else "N/A")
            else:
                 st.warning("Could not generate summary statistics.")

            st.subheader("Toxicity Distribution")
            score_cols = ['toxicity_score', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']
            dist_data = current_results_df[[col for col in score_cols if col in current_results_df.columns]].copy()
            if not dist_data.empty:
                dist_data_melted = dist_data.melt(var_name='Toxicity Type', value_name='Score')
                fig_hist = px.histogram(dist_data_melted, x='Score', color='Toxicity Type',
                                 title='Distribution of Toxicity Scores by Type',
                                 labels={'Score': 'Score (0-1)'},
                                 marginal="rug",
                                 barmode='overlay',
                                 opacity=0.7)
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("No toxicity scores to display yet.")

            st.subheader("Most Common Offensive Words")
            offensive_words_data = stats.get('most_common_offensive_words', {})
            if offensive_words_data:
                offensive_words_df = pd.DataFrame({
                    'word': list(offensive_words_data.keys()),
                    'count': list(offensive_words_data.values())
                })
                fig_bar = px.bar(offensive_words_df, x='word', y='count',
                             title='Top 10 Offensive Words',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No offensive words found or processed yet.")

            st.subheader("Detailed Results")
            st.dataframe(current_results_df)

            csv = current_results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="toxicity_analysis_results.csv",
                mime="text/csv",
            )

if __name__ == "__main__":
    main() 