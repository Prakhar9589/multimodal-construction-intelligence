# Multimodal Construction Intelligence Platform

A Streamlit capstone prototype for construction-site safety triage, visual crack diagnostics, project cost planning, real-estate valuation assumptions, and weather-aware site guidance.

## Features
- Gemini multimodal API integration with a password-masked API-key field.
- Demonstration mode when no key is configured or the AI request fails.
- PPE safety audit with JSON report download.
- Crack triage with uncertainty and engineering escalation warnings.
- Indicative cost, capex, asset-value, steel, and cement calculations.
- Weather-aware advisory and multi-turn site chatbot.
- No external database required.

## Run locally
Python 3.9+ is the requested baseline; Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Enter a Google Gemini API key in the sidebar to enable AI analysis. The app does not write the key to disk. Do not commit API keys to Git.

## Deploy to Streamlit Community Cloud
1. Push `app.py` and `requirements.txt` to a GitHub repository.
2. Create a new app in Streamlit Community Cloud and select `app.py`.
3. Deploy. A user may enter their key in the app sidebar.
4. For a shared/public deployment, prefer Streamlit secrets or a managed secrets store instead of asking users to enter a personal key.

## Important limitations
- AI vision output is not a certified safety inspection or structural diagnosis.
- Crack width from a single photo is unreliable unless a known scale and camera calibration are available.
- Cost, material quantity, and property valuation figures are illustrative assumptions. Replace with local schedule-of-rates, BOQ, site measurements, and comparable transactions.
- The planning tab provides an opt-in link to generate a conceptual image with Pollinations Flux. The prompt is sent to Pollinations when the link is opened; do not include confidential project or client information. Image generation is not rendered or stored in this app.
- OSHA and Indian standards differ by jurisdiction and work context. Have a qualified professional map the workflow to applicable local regulations and the project HSE plan.
