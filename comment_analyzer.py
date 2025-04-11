import os
import pandas as pd
from typing import Dict, List
import re
import time
from tqdm import tqdm
from dotenv import load_dotenv
import streamlit as st
import json
from groq import Groq, RateLimitError

class CommentAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=self.api_key)
        self.model = "gemma2-9b-it"
        self.request_interval = 3 # Minimum seconds between start of API calls
        self.last_request_time = 0

    def _rate_limit_wait(self):
        """Ensure we wait at least `self.request_interval` seconds between the start of API calls."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def analyze_comment(self, comment: str) -> Dict:
        """Analyze a single comment using Groq API with Gemma 2."""
        self._rate_limit_wait()

        prompt = f"""
        Analyze this comment for toxicity and offensive content. The comment is: "{comment}"

        Determine if it contains any of the following and provide scores from 0 to 1:
        - Toxicity
        - Severe toxicity
        - Obscene content
        - Threats
        - Insults
        - Identity hate

        Respond ONLY in valid JSON format (no introductory text, code fences, or explanations outside the JSON object) with the following structure:
        {{
            "is_toxic": boolean,
            "toxicity_score": float,
            "severe_toxicity": float,
            "obscene": float,
            "threat": float,
            "insult": float,
            "identity_hate": float,
            "offensive_words": list[string],
            "explanation": string
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=0.1, # Lower temperature for more predictable JSON
                response_format={"type": "json_object"}
            )

            content = chat_completion.choices[0].message.content
            analysis = json.loads(content)

            required_keys = {"is_toxic", "toxicity_score", "severe_toxicity", "obscene", "threat", "insult", "identity_hate", "offensive_words", "explanation"}
            if not required_keys.issubset(analysis.keys()):
                print(f"Warning: API response missing required keys. Got: {analysis.keys()}. Full response: {content}")
                raise ValueError(f"API response missing required keys.")

            return {
                'comment': comment,
                'cleaned_comment': self._clean_comment(comment),
                **analysis
            }
        except RateLimitError:
            st.warning("Rate limit likely reached. Waiting briefly before potential retry or error.")
            time.sleep(10) # Simple wait
            return self._get_error_response(comment, "Rate limit hit, waited 10s.")
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON response from API. Content: '{content}'. Error: {e}")
            st.error(f"Failed to parse API response: {e}")
            return self._get_error_response(comment, f"Failed to parse API JSON response: {e}")
        except Exception as e:
            import traceback
            print(f"Error analyzing comment: {comment[:100]}...")
            traceback.print_exc()
            st.error(f"Error analyzing comment: {str(e)}")
            return self._get_error_response(comment, str(e))

    def _get_error_response(self, comment: str, error_msg: str) -> Dict:
        """Return a standardized error response dictionary."""
        return {
            'comment': comment,
            'cleaned_comment': self._clean_comment(comment),
            'is_toxic': False,
            'toxicity_score': 0.0,
            'severe_toxicity': 0.0,
            'obscene': 0.0,
            'threat': 0.0,
            'insult': 0.0,
            'identity_hate': 0.0,
            'offensive_words': [],
            'explanation': f"Analysis Error: {error_msg}"
        }

    def _clean_comment(self, comment: str) -> str:
        """Basic text cleaning for comments."""
        if not isinstance(comment, str):
            return ""
        comment = comment.lower()
        comment = re.sub(r'http\S+|www\S+|https\S+', '', comment, flags=re.MULTILINE)
        comment = re.sub(r'[^\w\s]', ' ', comment) # Keep words and spaces
        comment = ' '.join(comment.split()) # Remove extra whitespace
        return comment

    def process_comments(self, comments: List[str], progress_bar=None) -> pd.DataFrame:
        """Process a list of comments sequentially, ensuring a minimum interval between API calls."""
        if not comments:
            return pd.DataFrame()

        results = []
        total_comments = len(comments)

        try:
            for i in tqdm(range(total_comments), desc="Processing comments", unit="comment", disable=(progress_bar is None)):
                comment = comments[i]
                if progress_bar:
                    progress_bar.progress((i + 1) / total_comments)

                result = self.analyze_comment(comment)
                results.append(result)

            return pd.DataFrame(results)

        except Exception as e:
            st.error(f"Error during processing: {str(e)}")
            import traceback
            print("--- Error during processing ---")
            traceback.print_exc()
            print("--- End Error Traceback ---")
            # Return any partially processed results
            return pd.DataFrame(results)

    def get_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics from the analysis DataFrame."""
        required_cols = ['is_toxic', 'toxicity_score', 'offensive_words']
        if df.empty or not all(col in df.columns for col in required_cols):
            return {
                'total_comments': 0,
                'toxic_comments': 0,
                'avg_toxicity': 0.0,
                'most_common_offensive_words': {}
            }

        # Safely process offensive words
        offensive_words_list = []
        for item in df['offensive_words'].dropna():
             if isinstance(item, list):
                 offensive_words_list.extend(item)

        avg_toxicity = df['toxicity_score'].mean() if pd.notna(df['toxicity_score']).any() else 0.0

        return {
            'total_comments': len(df),
            'toxic_comments': int(df['is_toxic'].sum()),
            'avg_toxicity': avg_toxicity,
            'most_common_offensive_words': pd.Series(offensive_words_list).value_counts().head(10).to_dict()
        }

    def get_toxicity_distribution(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Extract toxicity score distributions for plotting."""
        required_cols = ['toxicity_score', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']
        if df.empty or not all(col in df.columns for col in required_cols):
             return {col: [] for col in required_cols}

        return {col: df[col].fillna(0.0).tolist() for col in required_cols}