import json
import re
import io
import base64
from urllib.parse import quote
from datetime import datetime
from typing import Any, Dict

import streamlit as st
from PIL import Image

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

APP_NAME = "Multimodal Construction Intelligence Platform"
APP_VERSION = "1.0.0"
GEMINI_MODEL = "gemini-2.5-flash"

st.set_page_config(page_title=APP_NAME, page_icon="🏗️", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #f7f9fc 0%, #eef3f8 100%); }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1440px; }
    .hero { padding: 1.4rem 1.6rem; border-radius: 18px; color: white;
            background: linear-gradient(120deg, #102a43, #176b87); margin-bottom: 1rem; }
    .hero h1 { margin: 0 0 .35rem 0; font-size: 2rem; }
    .hero p { margin: 0; opacity: .92; }
    .card { padding: 1rem; background: white; border: 1px solid #e4eaf1;
            border-radius: 14px; box-shadow: 0 3px 14px rgba(16,42,67,.05); }
    .pill { display:inline-block; padding:.25rem .65rem; border-radius:999px;
            font-weight:700; font-size:.8rem; background:#e8f3fb; color:#145374; }
    .muted { color:#5b6b7a; font-size:.9rem; }
    div[data-testid="stMetric"] { background:white; padding: .9rem; border:1px solid #e4eaf1;
            border-radius:12px; }
    .disclaimer { padding:.8rem 1rem; border-left:4px solid #e0a526; background:#fff8e7;
            border-radius:8px; color:#604a12; font-size:.88rem; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
  <h1>🏗️ {APP_NAME}</h1>
  <p>Multimodal site intelligence · Safety audits · Crack triage · Cost planning · Weather-aware protocols</p>
</div>
""", unsafe_allow_html=True)

def demo_safety() -> Dict[str, Any]:
    return {
        "safety_score": 78,
        "overall_status": "Needs Attention",
        "ppe_detection": {
            "helmet": {"status": "Partially observed", "notes": "Demo result; verify each worker manually."},
            "high_visibility_vest": {"status": "Not clearly visible", "notes": "Demo result; visibility depends on image quality."},
            "steel_toe_boots": {"status": "Not verifiable from image", "notes": "Footwear cannot reliably be confirmed in this view."},
            "safety_harness": {"status": "Not applicable / not visible", "notes": "Assess only where work-at-height controls are required."}
        },
        "hazards": [
            {"hazard": "Unverified PPE compliance", "severity": "Medium",
             "remedy": "Conduct a close-range PPE check and record each worker before work starts."},
            {"hazard": "Potential housekeeping concern", "severity": "Low",
             "remedy": "Keep access routes clear and segregate materials from walkways."}
        ],
        "limitations": "Demonstration data only; no image model was called."
    }

def demo_crack() -> Dict[str, Any]:
    return {
        "defect_type": "Hairline",
        "estimated_crack_width_mm": None,
        "confidence": "Low",
        "root_causes": ["Could be shrinkage, surface curing, or a non-structural finish defect."],
        "recommended_repairs": ["Photograph with a scale and monitor for change.", "Have a qualified engineer inspect before selecting a repair."],
        "urgency": "Routine inspection",
        "red_flags": ["Do not infer structural safety from a photograph alone."],
        "limitations": "Demonstration data only; crack width cannot be measured reliably without scale/calibration."
    }

def extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        value = json.loads(text[start:end+1])
        if isinstance(value, dict):
            return value
    raise ValueError("The model response was not valid JSON.")

def ask_gemini(api_key: str, prompt: str, image: Image.Image = None, history=None) -> Dict[str, Any]:
    if not api_key or genai is None or types is None:
        raise RuntimeError("Gemini is unavailable or no API key was supplied.")
    client = genai.Client(api_key=api_key)
    contents = [prompt]
    if image is not None:
        img = image.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        contents.append(types.Part.from_bytes(data=buffer.getvalue(), mime_type="image/jpeg"))
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json")
    )
    return extract_json(response.text or "")

def json_download(data: Dict[str, Any], filename: str):
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button("⬇️ Download JSON report", data=payload, file_name=filename,
                       mime="application/json", use_container_width=False)

def show_json(data: Dict[str, Any]):
    st.json(data, expanded=True)

def money_inr(value: float) -> str:
    if value >= 1e7:
        return f"₹{value/1e7:.2f} Cr"
    if value >= 1e5:
        return f"₹{value/1e5:.2f} L"
    return f"₹{value:,.0f}"

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key = st.text_input("Google Gemini API key", type="password",
                            help="Used only for this app session. Do not paste your key into source code.")
    st.caption("No key? The app runs with clearly labelled demonstration outputs.")
    use_ai = bool(api_key.strip() and genai is not None)
    st.markdown("---")
    st.markdown("### Architecture")
    st.markdown("**UI:** Streamlit  \n**Vision / chat:** Gemini multimodal API  \n**Image handling:** Pillow  \n**State:** Streamlit session  \n**Storage:** No external database")
    st.markdown("---")
    st.markdown("### Feature navigation")
    st.markdown("1. Site Safety & PPE Audit  \n2. Crack Diagnostics  \n3. Planning & Valuation  \n4. Site Assistant & Weather")
    st.markdown("---")
    st.caption(f"Platform ID: 6ac4c98d1dcde6d7857c1642")
    st.caption(f"Version {APP_VERSION}")

tabs = st.tabs([
    "🦺 Site Safety & PPE Audit",
    "🧱 Crack Diagnostics",
    "📐 Planning & Valuation",
    "🌦️ Site Assistant & Weather"
])

with tabs[0]:
    st.subheader("Site Safety & PPE Audit")
    st.write("Upload a site photo to generate a preliminary PPE checklist and hazard register.")
    photo = st.file_uploader("Construction site photo", type=["jpg", "jpeg", "png"], key="safety_img")
    if photo:
        image = Image.open(photo)
        st.image(image, caption="Uploaded site image", use_container_width=True)
        if st.button("Run safety audit", type="primary", key="run_safety"):
            prompt = """Act as a cautious construction-site safety assistant. Inspect the supplied image and return ONLY valid JSON with this schema:
{
 "safety_score": integer 0-100,
 "overall_status": "Compliant" | "Needs Attention" | "High Risk" | "Unable to Assess",
 "ppe_detection": {
   "helmet":{"status":"Observed"|"Not observed"|"Unclear"|"Not applicable","notes":string},
   "high_visibility_vest":{"status":"Observed"|"Not observed"|"Unclear"|"Not applicable","notes":string},
   "steel_toe_boots":{"status":"Observed"|"Not observed"|"Unclear"|"Not applicable","notes":string},
   "safety_harness":{"status":"Observed"|"Not observed"|"Unclear"|"Not applicable","notes":string}
 },
 "hazards":[{"hazard":string,"severity":"Low"|"Medium"|"High"|"Critical","remedy":string}],
 "limitations":string
}
Only report visual evidence; do not infer hidden PPE. If not visible, use Unclear. Include OSHA/Indian construction-safety considerations as general guidance, but do not claim legal compliance certification. Image-based assessment is preliminary. Be concise."""
            with st.spinner("Reviewing image..."):
                try:
                    result = ask_gemini(api_key.strip(), prompt, image) if use_ai else demo_safety()
                    result["generated_at"] = datetime.now().isoformat(timespec="seconds")
                    result["mode"] = "Gemini AI" if use_ai else "Demonstration"
                    st.session_state["safety_result"] = result
                except Exception as e:
                    st.error(f"AI request failed: {e}. Showing demonstration output instead.")
                    result = demo_safety()
                    result["mode"] = "Demonstration fallback"
                    st.session_state["safety_result"] = result
    result = st.session_state.get("safety_result")
    if result:
        st.markdown("### Audit summary")
        c1, c2, c3 = st.columns(3)
        score = result.get("safety_score", 0)
        c1.metric("Safety score", f"{score}/100")
        c2.metric("Overall status", str(result.get("overall_status", "Unable to Assess")))
        c3.metric("Report mode", result.get("mode", "Unknown"))
        st.progress(max(0, min(100, int(score))) / 100)
        st.markdown("#### PPE checklist")
        ppe = result.get("ppe_detection", {})
        if isinstance(ppe, dict):
            cols = st.columns(2)
            for i, (name, detail) in enumerate(ppe.items()):
                with cols[i % 2]:
                    if isinstance(detail, dict):
                        st.markdown(f"**{name.replace('_',' ').title()}**")
                        st.markdown(f'<span class="pill">{detail.get("status","Unclear")}</span>', unsafe_allow_html=True)
                        st.caption(detail.get("notes", ""))
                    else:
                        st.write(f"**{name}:** {detail}")
        st.markdown("#### Identified hazards")
        hazards = result.get("hazards", [])
        if not hazards:
            st.info("No hazards were returned. This does not prove the site is hazard-free.")
        for hazard in hazards if isinstance(hazards, list) else []:
            if isinstance(hazard, dict):
                with st.container(border=True):
                    st.markdown(f"**{hazard.get('hazard','Hazard')}** · Severity: **{hazard.get('severity','Unknown')}**")
                    st.write(hazard.get("remedy", ""))
        st.caption(result.get("limitations", "Preliminary visual assessment only."))
        json_download(result, "site_safety_audit.json")

with tabs[1]:
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.write("Upload a wall or concrete photo. A photo cannot replace an on-site structural inspection.")
    crack_file = st.file_uploader("Concrete / wall image", type=["jpg", "jpeg", "png"], key="crack_img")
    scale_note = st.text_input("Optional scale / context", placeholder="e.g., ruler visible; exterior beam; crack appeared after rainfall")
    if crack_file:
        crack_image = Image.open(crack_file)
        st.image(crack_image, caption="Uploaded defect image", use_container_width=True)
        if st.button("Assess visible defect", type="primary", key="run_crack"):
            prompt = f"""Analyze the visible concrete/wall defect cautiously. Context from user: {scale_note or 'None provided'}.
Return ONLY JSON:
{{
 "defect_type":"Hairline"|"Settlement"|"Structural Shear"|"Thermal Expansion"|"Spalling"|"Other"|"Unable to Classify",
 "estimated_crack_width_mm": number or null,
 "confidence":"Low"|"Medium"|"High",
 "root_causes":[string],
 "recommended_repairs":[string],
 "urgency":"Routine inspection"|"Prompt engineer review"|"Urgent isolation and engineer review",
 "red_flags":[string],
 "limitations":string
}}
Do not claim to measure exact crack width unless a known scale is visible and usable. Otherwise set width null and explain. Never certify structural integrity from an image. Recommend a licensed structural engineer for diagonal/widening cracks, exposed/rebar-corroded concrete, displacement, sagging, or cracks in beams/columns."""
            with st.spinner("Assessing defect..."):
                try:
                    result = ask_gemini(api_key.strip(), prompt, crack_image) if use_ai else demo_crack()
                    result["generated_at"] = datetime.now().isoformat(timespec="seconds")
                    result["mode"] = "Gemini AI" if use_ai else "Demonstration"
                    st.session_state["crack_result"] = result
                except Exception as e:
                    st.error(f"AI request failed: {e}. Showing demonstration output instead.")
                    result = demo_crack()
                    result["mode"] = "Demonstration fallback"
                    st.session_state["crack_result"] = result
    result = st.session_state.get("crack_result")
    if result:
        a, b, c = st.columns(3)
        a.metric("Defect classification", result.get("defect_type", "Unknown"))
        width = result.get("estimated_crack_width_mm")
        b.metric("Estimated width", f"{width} mm" if width is not None else "Not measurable")
        c.metric("Confidence", result.get("confidence", "Unknown"))
        st.warning(f"Urgency: {result.get('urgency', 'Unknown')}")
        st.markdown("**Potential root causes**")
        for item in result.get("root_causes", []): st.write(f"• {item}")
        st.markdown("**Recommended next steps / repairs**")
        for item in result.get("recommended_repairs", []): st.write(f"• {item}")
        if result.get("red_flags"):
            st.markdown("**Red flags**")
            for item in result["red_flags"]: st.write(f"• {item}")
        st.caption(result.get("limitations", "Image assessment is not a structural certification."))
        json_download(result, "crack_diagnostics.json")

with tabs[2]:
    st.subheader("Project Planning & Real Estate Valuation")
    st.write("Illustrative planning calculator. Replace assumptions with local BOQ, rates, and comparable sales.")
    left, right = st.columns([1, 1])
    with left:
        structure = st.selectbox("Structure type", ["Residential house", "Apartment building", "Commercial building", "Warehouse"])
        area = st.number_input("Built-up area (sq ft)", min_value=100, max_value=500000, value=1100, step=50)
        tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
        completion = st.slider("Completion percentage", 0, 100, 35, 5)
        quality = st.selectbox("Construction finish", ["Basic", "Standard", "Premium"], index=1)
    rates = {
        "Residential house": {"Basic": 1500, "Standard": 1900, "Premium": 2500},
        "Apartment building": {"Basic": 1700, "Standard": 2200, "Premium": 3000},
        "Commercial building": {"Basic": 1800, "Standard": 2400, "Premium": 3400},
        "Warehouse": {"Basic": 900, "Standard": 1250, "Premium": 1700},
    }
    tier_factor = {"Tier 1": 1.25, "Tier 2": 1.0, "Tier 3": 0.82}[tier]
    build_rate = rates[structure][quality] * tier_factor
    total_budget = area * build_rate
    incurred = total_budget * completion / 100
    land_value_per_sqft = {"Tier 1": 5000, "Tier 2": 2800, "Tier 3": 1400}[tier]
    market_value = area * land_value_per_sqft + total_budget * 0.85
    steel_kg = area * (3.5 if structure == "Warehouse" else 4.0 if structure == "Residential house" else 4.5)
    cement_bags = area * (0.35 if structure == "Warehouse" else 0.40 if structure == "Residential house" else 0.45)
    with right:
        st.markdown("#### Estimate")
        st.metric("Indicative construction budget", money_inr(total_budget))
        st.metric("Capital expenditure incurred", money_inr(incurred))
        st.metric("Indicative asset value", money_inr(market_value))
        st.progress(completion / 100, text=f"Project milestone: {completion}% complete")
        m1, m2 = st.columns(2)
        m1.metric("Indicative steel", f"{steel_kg:,.0f} kg")
        m2.metric("Indicative cement", f"{cement_bags:,.0f} bags")
    st.markdown('<div class="disclaimer">These are illustrative assumptions, not a contractor quote, structural quantity take-off, bank valuation, or registered valuer opinion. Land value, location multiplier, and material quantities vary widely. Verify with a local engineer, quantity surveyor, and registered valuer.</div>', unsafe_allow_html=True)
    valuation = {
        "structure_type": structure, "built_up_area_sqft": area, "location_tier": tier,
        "finish": quality, "completion_percent": completion,
        "assumed_build_rate_inr_per_sqft": round(build_rate, 2),
        "estimated_total_budget_inr": round(total_budget, 2),
        "estimated_capex_incurred_inr": round(incurred, 2),
        "illustrative_market_asset_value_inr": round(market_value, 2),
        "indicative_steel_kg": round(steel_kg, 1),
        "indicative_cement_bags": round(cement_bags, 1),
        "disclaimer": "Illustrative estimate only; verify locally."
    }
    json_download(valuation, "project_planning_estimate.json")
    st.markdown("#### Conceptual 3D rendering prompt")
    render_prompt = st.text_area("Prompt for an external image generator",
        value=f"Photorealistic conceptual 3D architectural visualization of a {structure.lower()}, {area} sq ft built-up area, {quality.lower()} finish, Indian urban context ({tier}), realistic materials, daylight, front three-quarter view, no labels, not a construction drawing.",
        height=90, max_chars=1000)
    render_url = f"https://gen.pollinations.ai/image/{quote(render_prompt, safe='')}?model=flux&width=1024&height=768"
    st.link_button("Generate conceptual rendering with Pollinations", render_url, type="primary")
    st.caption("The link opens Pollinations and sends it your prompt. Do not include confidential project or client information.")

with tabs[3]:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Current / forecast condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    advisories = {
        "Normal": [
            "Run toolbox talk and confirm the day's work permits.",
            "Inspect access routes, scaffolds, lifting gear, and PPE before work.",
            "Follow approved drawings, method statements, and concrete curing requirements."
        ],
        "High Wind": [
            "Suspend crane lifts, hoisting, and work at height when site limits or manufacturer limits are exceeded.",
            "Secure loose sheets, formwork, signage, and stored materials; establish exclusion zones.",
            "Recheck scaffold stability and follow the site wind-speed trigger/action plan."
        ],
        "Heavy Rain": [
            "Stop work in flooded, unstable, or lightning-exposed areas; inspect excavations for water ingress and collapse risk.",
            "Isolate electrical equipment exposed to water; use RCD/GFCI protection and qualified electrical inspection.",
            "Protect fresh concrete from washout and follow the engineer-approved curing / pour plan; do not add water arbitrarily."
        ],
        "Extreme Heat": [
            "Schedule strenuous work in cooler periods, provide shade, drinking water, and rest breaks.",
            "Use a buddy system and monitor for heat exhaustion / heat stroke; stop work and seek urgent help for symptoms.",
            "Protect concrete from rapid moisture loss and follow the approved hot-weather concreting and curing procedure."
        ]
    }
    for item in advisories[weather]:
        st.info(item)
    st.caption("Weather actions must follow the project HSE plan, equipment limits, local forecasts, and competent-person instructions.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_prompt = st.chat_input("Ask about construction planning, site safety, materials, or procedures...")
    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        with st.chat_message("assistant"):
            if use_ai:
                context = "\n".join([f'{m["role"]}: {m["content"]}' for m in st.session_state.chat_history[-8:]])
                prompt = f"""You are a cautious construction project assistant. Current weather condition selected: {weather}.
Answer the user's construction question in practical, clear language. Ask clarifying questions when essential. Do not replace licensed engineering, local codes, site-specific method statements, or emergency services. Do not invent code clauses or claim that a photo certifies safety.
Conversation:
{context}
Respond in plain text."""
                try:
                    client = genai.Client(api_key=api_key.strip())
                    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
                    answer = response.text or "I could not generate a response. Please try again."
                except Exception as e:
                    answer = f"AI is temporarily unavailable ({e}). General reminder: follow approved drawings, local codes, and a competent engineer's site-specific instructions."
            else:
                answer = ("Demo mode: I can help with general construction planning and safety concepts when a Gemini API key is configured. "
                          "For now, follow the approved drawings, project HSE plan, local building rules, and a qualified engineer's advice. "
                          f"Selected weather condition: {weather}.")
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.markdown(
    '<p class="muted">Important: This is a decision-support prototype, not a substitute for a competent safety officer, structural engineer, quantity surveyor, registered valuer, or local authority. AI outputs can be incorrect; verify before taking action.</p>',
    unsafe_allow_html=True
)
