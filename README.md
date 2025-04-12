# Comment Moderation System (Groq/Gemma 2)

**This project's GitHub repository is available for reference, but you can directly access the deployed application here: [Hate Comment Detector](https://hate-comment-detector.streamlit.app/)**

---

A Python application built with Streamlit that uses Groq Cloud's Gemma 2 model to detect and analyze toxicity in user comments. The system provides a user-friendly web interface for uploading comment data (CSV or JSON), analyzing comments sequentially, viewing analysis results, and exporting the findings.

## Features

-   Load and process comments from CSV or JSON files via a Streamlit web interface.
-   Detect toxicity using the `gemma2-9b-it` model via the Groq API.
-   Provides scores (0-1) for: Toxicity, Severe Toxicity, Obscene, Threat, Insult, Identity Hate.
-   Identifies potentially offensive words within comments.
-   Processes comments sequentially, ensuring a minimum **3-second interval** between the start of each API call to respect potential rate limits.
-   Displays summary statistics (total comments, toxic comments, average toxicity) and visualizations (toxicity distribution histogram, common offensive words bar chart).
-   Allows exporting analyzed data (including toxicity scores and explanations) in CSV format.
-   Interactive web interface using Streamlit for easy file upload and result browsing.
-   Progress bar indicates analysis progress during sequential processing.

## Prerequisites (for local development)

-   Python 3.8 or higher
-   Groq API key (sign up at [https://console.groq.com/](https://console.groq.com/))
-   Required Python packages (listed in `requirements.txt`)

## Installation (for local development)

1.  Clone this repository:
    ```bash
    git clone https://github.com/Raj-Shriwastav/Hate-Speech-Detector.git
    cd Hate-Speech-Detector
    ```

2.  Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  Create a `.env` file in the project root directory and add your Groq API key:
    ```dotenv
    GROQ_API_KEY=your_groq_api_key_here
    ```

## Usage (for local development)

1.  Ensure your `.env` file is correctly set up with your Groq API key.

2.  Start the Streamlit application from your terminal:
    ```bash
    streamlit run app.py
    ```

3.  Open your web browser and navigate to the local URL provided in the terminal (usually `http://localhost:8501`).

4.  Use the file uploader in the web app to select your comments file (must be CSV or JSON).

5.  The application will:
    *   Validate the file and check for the required `comment_text` column.
    *   If the file is valid, enable the "Start Processing All Comments" button.
    *   Click the button to start the analysis. Comments will be processed one by one, with a minimum 3-second delay between the start of each analysis request.
    *   Display a progress bar showing the overall analysis progress.
    *   Once processing begins (or completes), it displays overall summary statistics and charts (toxicity distribution, common offensive words).
    *   Show a table with detailed results for all processed comments, including scores and explanations.
    *   Provide a button to download the complete results as a CSV file (`toxicity_analysis_results.csv`).
    *   Allow uploading a new file at any time (this will reset the application state).

## Input File Format

The input file must be either CSV or JSON and **must** contain a column/field named `comment_text`. Other fields (e.g., `comment_id`, `username`) are optional but will be preserved in the output if present.

**Example CSV (`comments.csv`):**
```csv
comment_id,username,comment_text
1,user1,"This is a perfectly fine comment."
2,user2,"This one contains hate speech!"
3,user3,"What an insult this is."
```

**Example JSON (`comments.json`):**
```json
[
  {
    "comment_id": 1,
    "username": "user1",
    "comment_text": "This is a perfectly fine comment."
  },
  {
    "comment_id": 2,
    "username": "user2",
    "comment_text": "This one contains hate speech!"
  },
  {
    "comment_id": 3,
    "username": "user3",
    "comment_text": "What an insult this is."
  }
]
```

## Output

The application displays the analysis results in the Streamlit interface and allows downloading a CSV file (`toxicity_analysis_results.csv`) containing the original data plus the following analysis fields for each comment, as provided by the Gemma 2 model via Groq:

-   `comment`: The original comment text.
-   `cleaned_comment`: (str) A processed version of the original comment used for analysis.
-   `is_toxic`: (boolean) True if the model considers the comment toxic.
-   `toxicity_score`: (float 0-1) Overall toxicity score.
-   `severe_toxicity`: (float 0-1) Score for severe toxicity.
-   `obscene`: (float 0-1) Score for obscene content.
-   `threat`: (float 0-1) Score for threatening content.
-   `insult`: (float 0-1) Score for insulting content.
-   `identity_hate`: (float 0-1) Score for identity hate.
-   `offensive_words`: (list[str]) List of words identified as potentially offensive by the model.
-   `explanation`: (str) The model's explanation for its analysis (can sometimes include errors if analysis failed).

## Sample Output CSV (`toxicity_analysis_results.csv`)

```csv
comment_id,username,comment_text,cleaned_comment,is_toxic,toxicity_score,severe_toxicity,obscene,threat,insult,identity_hate,offensive_words,explanation
1,user1,"This is a perfectly fine comment.",this is a perfectly fine comment,False,0.05,0.01,0.02,0.01,0.03,0.01,"[]","The comment is neutral and does not contain offensive language."
2,user2,"This one contains hate speech!",this one contains hate speech,True,0.95,0.8,0.1,0.05,0.2,0.9,"['hate speech']","The comment contains explicit hate speech targeting a group."
3,user3,"What an insult this is.",what an insult this is,True,0.8,0.1,0.1,0.02,0.85,0.05,"['insult']","The comment is a direct insult."
```

*(Note: Sample output values are illustrative)*
