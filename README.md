# prompt_enh_api
EFMNB Prompt Optimizer (Gemini + PCV)

EFMNB Prompt Optimizer is a Streamlit-based application for analyzing and improving prompts using a deterministic multi-step PCV pipeline (Proposer → Critic → Verifier).
The system integrates with the Google Gemini API to deliver stable, structured, and constraint-driven prompt optimization.
It evaluates text using the EFMNB framework and rewrites prompts through 12 sequential PCV steps for maximal clarity and reliability.

Features
EFMNB Text Analysis

The application evaluates prompts along five axes:

E — Emotion

F — Factuality and specificity

M — Meta-instruction density

N — Narrative or reasoning structure

B — Bias or subjective framing

Outputs include:

Strict JSON response

Radar chart visualization

Heatmap visualization

PCV-Based Prompt Optimization (4 Full Cycles)

Implements a deterministic 12-step pipeline:

Proposer rewrites the prompt

Critic identifies structural issues and risks

Verifier corrects the prompt using the Critic’s findings

One cycle = 3 LLM calls → Four cycles = 12 API calls per optimization.
This approach ensures structural consistency and minimizes ambiguity or hallucination.

Gemini API Integration

Supports all Gemini models (default: gemini-2.5-flash)

Direct low-level API calls

No external SDK dependencies

Batch Mode

Line-by-line EFMNB analysis of uploaded text files

JSON export

Batch radar and heatmap visualizations

Installation
1. Clone the repository
git clone https://github.com/your-username/efmnb-prompt-optimizer.git
cd efmnb-prompt-optimizer

2. Install dependencies
pip install -r requirements.txt

3. Set your Gemini API key

Create a .env file or export manually:

export GEMINI_API_KEY="your_api_key_here"

4. Run the application
streamlit run promptenh_pcv_gemini.py

Usage
Single Prompt Mode

Paste an input prompt

Run EFMNB analysis

Visualize the score profile

Execute the PCV × 4 optimization cycle

Download the improved prompt as plain text

Batch Analysis Mode

Upload a .txt file (1 item per line)

Receive EFMNB scores for each entry

Export results as JSON

Architecture Overview

The system includes the following components:

EFMNB Analyzer
Generates a structured JSON evaluation of a text using fixed rules.

PCV Pipeline
A deterministic chain of 12 LLM interactions implementing:

Proposer → Critic → Verifier

Executed four times to ensure convergence on a stable prompt.

Gemini Interface
Thin wrapper around the REST API for generateContent operations.

Streamlit UI
Provides interactive prompt input, visualizations, and output tools.

Why PCV?

Typical LLM-based prompt improvement is inconsistent.
The PCV method forces:

Recursive refinement

Structured criticism

Explicit correction

Stability across iterations

This dramatically reduces ambiguity, increases determinism, and yields high-quality system prompts suitable for production use.
ChatGPT сказал:

Here’s a clean, professional README.md for your repository.
Без моих привычных комментариев — только технический документ, как и просил.

EFMNB Prompt Optimizer (Gemini + PCV)

EFMNB Prompt Optimizer is a Streamlit-based application for analyzing and improving prompts using a deterministic multi-step PCV pipeline (Proposer → Critic → Verifier).
The system integrates with the Google Gemini API to deliver stable, structured, and constraint-driven prompt optimization.
It evaluates text using the EFMNB framework and rewrites prompts through 12 sequential PCV steps for maximal clarity and reliability.

Features
EFMNB Text Analysis

The application evaluates prompts along five axes:

E — Emotion

F — Factuality and specificity

M — Meta-instruction density

N — Narrative or reasoning structure

B — Bias or subjective framing

Outputs include:

Strict JSON response

Radar chart visualization

Heatmap visualization

PCV-Based Prompt Optimization (4 Full Cycles)

Implements a deterministic 12-step pipeline:

Proposer rewrites the prompt

Critic identifies structural issues and risks

Verifier corrects the prompt using the Critic’s findings

One cycle = 3 LLM calls → Four cycles = 12 API calls per optimization.
This approach ensures structural consistency and minimizes ambiguity or hallucination.

Gemini API Integration

Supports all Gemini models (default: gemini-2.5-flash)

Direct low-level API calls

No external SDK dependencies

Batch Mode

Line-by-line EFMNB analysis of uploaded text files

JSON export

Batch radar and heatmap visualizations

Installation
1. Clone the repository
git clone https://github.com/your-username/efmnb-prompt-optimizer.git
cd efmnb-prompt-optimizer

2. Install dependencies
pip install -r requirements.txt

3. Set your Gemini API key

Create a .env file or export manually:

export GEMINI_API_KEY="your_api_key_here"

4. Run the application
streamlit run promptenh_pcv_gemini.py

Usage
Single Prompt Mode

Paste an input prompt

Run EFMNB analysis

Visualize the score profile

Execute the PCV × 4 optimization cycle

Download the improved prompt as plain text

Batch Analysis Mode

Upload a .txt file (1 item per line)

Receive EFMNB scores for each entry

Export results as JSON

Architecture Overview

The system includes the following components:

EFMNB Analyzer
Generates a structured JSON evaluation of a text using fixed rules.

PCV Pipeline
A deterministic chain of 12 LLM interactions implementing:

Proposer → Critic → Verifier

Executed four times to ensure convergence on a stable prompt.

Gemini Interface
Thin wrapper around the REST API for generateContent operations.

Streamlit UI
Provides interactive prompt input, visualizations, and output tools.

Why PCV?

Typical LLM-based prompt improvement is inconsistent.
The PCV method forces:

Recursive refinement

Structured criticism

Explicit correction

Stability across iterations

This dramatically reduces ambiguity, increases determinism, and yields high-quality system prompts suitable for production use.

File Structure
/efmnb-prompt-optimizer
│
├── promptenh_pcv_gemini.py    # Main Streamlit application
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
└── /images                    # (Optional) Screenshots and diagrams

Requirements

Python 3.9+

Streamlit

Plotly

Pandas

Requests

Google Gemini API key

License

MIT License.
You are free to modify, extend, and distribute this project.

Contributions

Pull requests and feature suggestions are welcome, especially for:

Additional validation frameworks

Alternative optimization pipelines

UI/UX improvements

Support for multiple LLM providers
