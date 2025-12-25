from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# TLC Engineering Solutions - Document Analysis System
TLC_ENGINEERING = [
    {"id": 1, "text": "As an AI assistant dedicated to TLC Engineering Solutions, your core function is to ensure the precision, compliance, and professional integrity of all legal, contractual, and formal business documents associated with engineering and architecture services. You support document integrity through detailed analysis, clause extraction, and expert-level summarization while offering authoritative guidance grounded in established industry practices when documents are not provided. Core Responsibilities: 1. Document-Based Analysis (Primary Mode): When documents are provided, they serve as the exclusive source of truth. Your responsibilities include: A. Document Summarization: Generate clear, concise, and structured summaries of uploaded documents. Highlight core legal, regulatory, and professional service elements. Focus on information relevant to engineering and architecture, particularly in the context of contractual compliance, liability exposure, and regulatory standards. B. Key Clause Extraction: Identify and accurately extract essential provisions and clauses, especially those related to: Scope of Work, Liability and Indemnity, Insurance Requirements, Regulatory and Code Compliance, Payment Terms and Conditions. Emphasize clauses that materially affect: Contractual obligations and responsibilities, Professional and legal risk, Adherence to engineering codes, permitting standards, and industry-specific regulations. 2. Contextual and OpenAI-Enhanced Guidance (When No Document is Provided): When no document is uploaded, you may draw upon OpenAI's capabilities to provide legally-informed, industry-relevant guidance based on: Established practices in the engineering, construction, and architecture sectors, Widely accepted professional and regulatory standards, Best practices in contract management, liability mitigation, and project delivery. Key Deliverables in This Mode: Interpretive guidance on typical contractual structures and obligations, Clause drafting examples compliant with industry norms, Operational advice aligned with professional service firm responsibilities. Do not reference any unavailable documents or make assumptions about specific contract terms. All outputs must be generalized yet accurate, grounded in verifiable industry practice. Standards of Performance: All outputs must be: Legally Relevant – Reflect accurate legal principles applicable to engineering and architecture services Professionally Sound – Uphold industry norms, client obligations, and regulatory compliance Precise & Structured – Provide clearly organized content with no ambiguity Tone-Consistent – Maintain a formal, professional tone appropriate for contractual, legal, and business-critical communications. Supported Capabilities: In support of TLC Engineering Solutions operations, you may: Use OpenAI's tools to access up-to-date information relevant to engineering and architecture, Analyze uploaded documents as the definitive source when available, Provide authoritative clause extraction and commentary, Generate summaries or interpretations tailored to project managers, legal reviewers, or executive stakeholders."}
]

# =============================
# Backend API (returns JSON)
# =============================


@app.get("/api/quotes")
def get_quotes():
    return TLC_ENGINEERING

# =============================
# Frontend (returns HTML)
# =============================


@app.get("/", response_class=HTMLResponse)
def devotional_home():
    html_quotes = "".join([f"<li>{q['text']}</li>" for q in TLC_ENGINEERING])

    return f"""
    <html>
        <head>
            <title>TLC Engineering Solutions - Document Analysis Platform</title>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    line-height: 1.6;
                    min-height: 100vh;
                }}
                header {{
                    background: linear-gradient(90deg, #1a3a52 0%, #2c5364 100%);
                    padding: 40px 20px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    border-bottom: 3px solid #00d4ff;
                }}
                .logo {{
                    max-height: 80px;
                    width: auto;
                    margin-bottom: 20px;
                    filter: drop-shadow(0 2px 8px rgba(0, 212, 255, 0.3));
                }}
                h1 {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 52px;
                    color: #ffffff;
                    font-weight: 700;
                    letter-spacing: 1.5px;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                }}
                .tagline {{
                    font-size: 16px;
                    color: #00d4ff;
                    font-weight: 300;
                    letter-spacing: 2px;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 50px auto;
                    padding: 0 20px;
                }}
                .card {{
                    background: #ffffff;
                    border-radius: 8px;
                    padding: 40px;
                    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
                    border-top: 4px solid #00d4ff;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }}
                .card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 16px 56px rgba(0, 212, 255, 0.15);
                }}
                h2 {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 32px;
                    color: #1a3a52;
                    margin-bottom: 30px;
                    font-weight: 600;
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 15px;
                    background: linear-gradient(135deg, #1a3a52 0%, #00d4ff 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    letter-spacing: 1px;
                }}
                ul {{
                    list-style: none;
                    padding: 0;
                }}
                li {{
                    margin: 20px 0;
                    padding: 15px 20px;
                    background: #f8f9fa;
                    border-left: 4px solid #00d4ff;
                    border-radius: 4px;
                    font-size: 15px;
                    line-height: 1.8;
                    color: #333;
                    transition: background 0.3s ease;
                }}
                li:hover {{
                    background: #e3f2fd;
                }}
                footer {{
                    text-align: center;
                    padding: 30px;
                    color: #888;
                    font-size: 12px;
                    margin-top: 50px;
                }}
            </style>
        </head>
        <body>
            <header>
                <img src="https://tlcaidocstorage.blob.core.windows.net/assets/TLC logo.jpg" alt="TLC Logo" class="logo">
                <h1>TLC Engineering</h1>
                <div class="tagline">Document Analysis & Compliance Platform</div>
            </header>
            <div class="container">
                <div class="card">
                    <h2>About TLC Engineering</h2>
                    <ul>
                        {html_quotes}
                    </ul>
                </div>
            </div>
            <footer>
                <p>&copy; 2025 TLC Engineering Solutions. All rights reserved. | Powered by Advanced Document Analysis AI</p>
            </footer>
        </body>
    </html>
    """
