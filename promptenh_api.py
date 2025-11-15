import json
import re
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# =========================
# Basic config
# =========================

st.set_page_config(page_title="EFMNB Prompt Optimizer (Gemini + PCV)", layout="wide")
st.title("EFMNB Prompt Optimizer (Gemini API, PCV x4)")

AXES = ["E", "F", "M", "N", "B"]

# =========================
# EFMNB ANALYZER PROMPT
# =========================

ANALYZER_PROMPT = """You are an analytical model that evaluates a text on five axes (EFMNB). 
Return ONE strict JSON object only.

You MUST output a single JSON object with exactly these keys:
"E", "F", "M", "N", "B", "summary"

Value requirements:
- E, F, M, N, B: numbers in [0,1]
- summary: short string (1–3 sentences)
- No extra keys, no markdown, no explanations, no comments.

Axis definitions (rate the text AS IT IS):

E — emotional intensity  
F — factual specificity  
M — meta-instruction density  
N — narrative or reasoning flow  
B — bias or one-sided framing  

Return ONLY JSON.

Text:
<<<TEXT>>>"""

# =========================
# PCV TEMPLATES
# =========================

PROPOSER_TEMPLATE = """You are PROPOSER, a precise prompt engineer.
Your task is to rewrite the following prompt so that it becomes:
- clearer and less ambiguous,
- more constrained and deterministic,
- explicit about steps and output format,
- safer against hallucinations.

Rules:
- Preserve the original task and user intent.
- Do NOT add external facts or assumptions.
- Reduce emotional or rhetorical language unless required.
- Avoid marketing tone; keep it technical and neutral.
- Do NOT use markdown; output plain text only.
- Output ONLY the rewritten prompt.

Original prompt:
<<<PROMPT>>>"""

CRITIC_TEMPLATE = """You are CRITIC, a strict prompt reviewer.
Analyze the following prompt and return ONLY a bullet-style list of issues and improvement suggestions.

Focus on:
- Ambiguous or vague wording.
- Missing constraints, edge cases, or unclear input/output requirements.
- Lack of explicit structure, steps, or output format.
- Risks of hallucinations (where the model might invent facts).
- Unnecessary emotional tone or bias that does not serve the task.

If you find no meaningful issues, still output a short confirmation like:
- No critical issues found, only minor refinements possible.

Prompt to review:
<<<PROMPT>>>"""

VERIFIER_TEMPLATE = """You are VERIFIER, a corrective prompt optimizer.
You receive:
1) a draft prompt (Version A),
2) a CRITIC-REPORT with issues and suggested improvements.

Your task:
- Rewrite the prompt, producing a new version that fixes EVERY listed issue.
- Preserve the original task and intent.
- Do NOT add fictional facts or external context.
- Make constraints, structure, and expectations explicit and deterministic.
- Avoid emotional language and subjective bias unless explicitly required.
- Do NOT use markdown; output plain text only.
- Output ONLY the improved prompt text.

Version A:
<<<PROMPT>>>

CRITIC-REPORT:
<<<REPORT>>>"""

# =========================
# Gemini low-level helper
# =========================

def call_gemini(api_key: str, model: str, prompt: str) -> str:
    """
    Один низкоуровневый вызов Gemini: models/{model}:generateContent
    Возвращает просто текст ответа (или сырое тело JSON в крайнем случае).
    """
    if not api_key:
        raise RuntimeError("Gemini API key is missing")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    r = requests.post(url, json=body, timeout=120)
    try:
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}, response={r.text[:500]}")

    data = r.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        # если внезапно другой формат – хоть что-то вернём
        return json.dumps(data, ensure_ascii=False)

# =========================
# PCV STEPS
# =========================

def proposer_step(api_key: str, model: str, prompt_text: str) -> str:
    prompt = PROPOSER_TEMPLATE.replace("<<<PROMPT>>>", prompt_text)
    resp = call_gemini(api_key, model, prompt)
    return resp.strip()

def critic_step(api_key: str, model: str, draft_prompt: str) -> str:
    prompt = CRITIC_TEMPLATE.replace("<<<PROMPT>>>", draft_prompt)
    resp = call_gemini(api_key, model, prompt)
    return resp.strip()

def verifier_step(api_key: str, model: str, draft_prompt: str, critic_report: str) -> str:
    prompt = (
        VERIFIER_TEMPLATE
        .replace("<<<PROMPT>>>", draft_prompt)
        .replace("<<<REPORT>>>", critic_report)
    )
    resp = call_gemini(api_key, model, prompt)
    return resp.strip()

# =========================
# EFMNB ANALYSIS
# =========================

def call_gemini_analyze(api_key: str, model: str, text: str) -> dict:
    prompt = ANALYZER_PROMPT.replace("<<<TEXT>>>", text)
    resp = call_gemini(api_key, model, prompt)

    # аккуратно парсим JSON
    try:
        obj = json.loads(resp)
    except Exception:
        s = resp.replace("```json", "").replace("```", "")
        m = re.search(r"\{[\s\S]*\}", s)
        if not m:
            raise RuntimeError(f"No JSON in output: {resp[:300]}")
        obj = json.loads(m.group(0))

    for k in AXES:
        obj[k] = float(obj.get(k, 0))
        obj[k] = max(0.0, min(1.0, obj[k]))

    obj["summary"] = str(obj.get("summary", "")).strip()
    return obj

# =========================
# PCV LOOP (4 * [P, C, V] = 12 calls)
# =========================

def call_gemini_improve(api_key: str, model: str, original_prompt: str) -> str:
    """
    Запускает 4 полных цикла:
    [Proposer -> Critic -> Verifier] * 4 = 12 вызовов модели.
    Без раннего выхода, даже если Critic скажет 'всё ок'.
    """
    current = original_prompt.strip()
    for _ in range(4):
        draft = proposer_step(api_key, model, current)
        report = critic_step(api_key, model, draft)
        improved = verifier_step(api_key, model, draft, report)
        current = improved.strip()
    return current

# =========================
# Sidebar
# =========================

with st.sidebar:
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    gemini_model = st.text_input("Gemini model name", "gemini-2.5-flash")
    theme_dark = st.toggle("Dark theme", True)
    tmpl = "plotly_dark" if theme_dark else "plotly_white"
    st.markdown("---")
    st.markdown(
        "Uses Google Gemini API for EFMNB analysis and **PCV-based prompt rewriting** "
        "(4 × [Proposer, Critic, Verifier] = 12 calls per improvement)."
    )

# =========================
# Layout: tabs
# =========================

tab1, tab2 = st.tabs(["Single prompt (analyze & improve)", "Batch analysis"])

# =========================
# TAB 1: Single prompt
# =========================

with tab1:
    st.subheader("1. Enter original prompt")

    prompt_text = st.text_area(
        "Original prompt",
        height=220,
        placeholder="Paste the prompt you want to analyze and improve.",
    )

    analyze_clicked = st.button("Analyze EFMNB", type="primary")

    if analyze_clicked:
        if not prompt_text.strip():
            st.error("Prompt is empty.")
        else:
            try:
                res = call_gemini_analyze(gemini_api_key, gemini_model, prompt_text)
            except Exception as e:
                st.error(f"Gemini analysis error: {e}")
            else:
                st.session_state["analysis"] = res
                st.session_state["original_prompt"] = prompt_text
                st.session_state.pop("improved_prompt", None)

    if "analysis" in st.session_state:
        res = st.session_state["analysis"]

        st.subheader("2. EFMNB analysis result")

        df_single = pd.DataFrame(
            [{"label": "prompt", **{k: res[k] for k in AXES}}]
        )

        c1, c2 = st.columns([1, 1])

        with c1:
            st.json(res)
            st.download_button(
                "Download JSON",
                json.dumps(res, ensure_ascii=False, indent=2),
                "efmnb_analysis.json",
            )

        with c2:
            categories = AXES
            vals = [df_single.iloc[0][c] for c in categories]

            fig_r = go.Figure()
            fig_r.add_trace(
                go.Scatterpolar(
                    r=vals + vals[:1],
                    theta=categories + categories[:1],
                    fill="toself",
                    name="prompt",
                )
            )
            fig_r.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                template=tmpl,
                height=420,
                title="Radar: EFMNB profile",
            )
            st.plotly_chart(fig_r, use_container_width=True)

        st.markdown("---")
        st.subheader("3. Improve prompt via PCV (4 × [Proposer, Critic, Verifier])")

        improve_clicked = st.button("Generate improved prompt (PCV x4)")

        if improve_clicked:
            original = st.session_state.get("original_prompt", "").strip()
            if not original:
                st.error("Original prompt is missing. Re-run analysis.")
            else:
                try:
                    improved = call_gemini_improve(gemini_api_key, gemini_model, original)
                except Exception as e:
                    st.error(f"Gemini improvement error: {e}")
                else:
                    st.session_state["improved_prompt"] = improved

        if "improved_prompt" in st.session_state:
            st.text_area(
                "Improved prompt",
                st.session_state["improved_prompt"],
                height=260,
            )
            st.download_button(
                "Download improved prompt",
                st.session_state["improved_prompt"],
                "improved_prompt.txt",
            )

# =========================
# TAB 2: Batch EFMNB only
# =========================

with tab2:
    st.subheader("Batch EFMNB analysis")

    left, right = st.columns([1, 1])

    with left:
        up = st.file_uploader("Upload texts.txt (one per line)", type=["txt"])
        demo = st.toggle("Use demo batch", value=True)

        run_batch = st.button("Run batch analysis")

        if run_batch:
            rows = []
            if up:
                content = up.read().decode("utf-8-sig")
                for i, line in enumerate(content.splitlines(), 1):
                    if line.strip():
                        rows.append((f"row_{i}", line.strip()))
            elif demo:
                rows = [
                    ("Fiction", "Darkness descends upon the city, and a lone witness must choose between truth and safety."),
                    ("News", "The agency reported a 3.2% increase in quarterly revenue compared to last year."),
                    ("Academic", "Recent work formalizes robustness via distributional shift and proposes causal regularization."),
                ]

            if not rows:
                st.error("No data to analyze.")
            else:
                out = []
                for label, txt in rows:
                    try:
                        r = call_gemini_analyze(gemini_api_key, gemini_model, txt)
                    except Exception as e:
                        st.error(f"Error on {label}: {e}")
                        break
                    out.append(
                        {
                            "label": label,
                            **{k: r[k] for k in AXES},
                            "summary": r["summary"],
                        }
                    )

                if out:
                    dfb = pd.DataFrame(out)
                    st.dataframe(dfb, use_container_width=True, hide_index=True)
                    st.download_button(
                        "Download batch JSON",
                        json.dumps(out, ensure_ascii=False, indent=2),
                        "efmnb_batch.json",
                    )

                    cats = AXES
                    figR = go.Figure()
                    for _, row in dfb.iterrows():
                        v = [row[c] for c in cats]
                        figR.add_trace(
                            go.Scatterpolar(
                                r=v + v[:1],
                                theta=cats + cats[:1],
                                fill="toself",
                                name=str(row["label"]),
                            )
                        )
                    figR.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        template=tmpl,
                        height=520,
                        title="Radar (batch)",
                    )
                    st.plotly_chart(figR, use_container_width=True)
