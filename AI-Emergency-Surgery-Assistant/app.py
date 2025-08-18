import os
import gradio as gr
from anthropic import Anthropic
import requests
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Load environment variables
load_dotenv()

# Configuration via environment with sensible defaults for local dev
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
MODAL_CLINIC_ENDPOINT = os.getenv(
    "MODAL_CLINIC_ENDPOINT",
    "https://aayushraj0324--healthmate-clinic-lookup-search-clinics.modal.run",
)

# Initialize Anthropic client (optional if no key provided)
client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

def classify_urgency(symptoms: str) -> str:
    """Classify the urgency level of the symptoms using Claude."""
    if not client:
        return (
            "AI analysis unavailable: Missing ANTHROPIC_API_KEY. "
            "Add it to a .env file to enable urgency classification."
        )
    prompt = (
        f"You are a medical triage assistant. Given this symptom description: {symptoms}, "
        "\nclassify it as: emergency / routine visit / home care. Explain briefly."
    )
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=150,
        temperature=0.1,
        system="You are a medical triage assistant. Provide clear, concise classifications.",
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

def get_possible_conditions(symptoms: str) -> str:
    """Get possible medical conditions based on symptoms using Claude."""
    if not client:
        return (
            "AI analysis unavailable: Missing ANTHROPIC_API_KEY. "
            "Add it to a .env file to see possible conditions."
        )
    prompt = (
        f"List 2–4 possible medical conditions that match these symptoms: {symptoms}. "
        "\nKeep it non-technical and easy to understand."
    )
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=200,
        temperature=0.1,
        system="You are a medical assistant. Provide clear, non-technical explanations of possible conditions.",
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

def lookup_clinics(city: str) -> str:
    """Lookup clinics via remote endpoint, with a local DuckDuckGo fallback."""
    if not city:
        return "Please provide a city to find nearby clinics."

    # Try remote service first if configured
    if MODAL_CLINIC_ENDPOINT:
        try:
            response = requests.get(
                MODAL_CLINIC_ENDPOINT, params={"city": city}, timeout=20
            )
            response.raise_for_status()
            clinics = response.json()
            if clinics and isinstance(clinics, list) and "error" not in clinics[0]:
                return "\n\n".join(
                    [
                        f"🏥 {clinic['name']}\n🔗 {clinic['link']}\n📝 {clinic['description']}"
                        for clinic in clinics
                    ]
                )
            else:
                # If remote returns an error, fall through to local search
                pass
        except Exception:
            # Network or service error; fall back to local DDG search
            pass

    # Local fallback using DuckDuckGo
    try:
        with DDGS() as ddgs:
            search_query = f"top medical clinics near {city}"
            results = list(ddgs.text(search_query, max_results=3))
            if not results:
                return f"No clinics found near {city}."
            return "\n\n".join(
                [
                    f"🏥 {r.get('title', 'Unknown Clinic')}\n"
                    f"🔗 {r.get('link', '#')}\n"
                    f"📝 {r.get('body', 'No description available')}"
                    for r in results
                ]
            )
    except Exception as e:
        return f"Error searching for clinics locally: {str(e)}"

def process_input(symptoms: str, city: str) -> tuple:
    """Process the input and return all results."""
    # Get urgency classification
    urgency = classify_urgency(symptoms)
    
    # Get possible conditions
    conditions = get_possible_conditions(symptoms)
    
    # Get nearby clinics if city is provided
    if city:
        clinic_text = lookup_clinics(city)
    else:
        clinic_text = "Please provide a city to find nearby clinics."
    
    return urgency, conditions, clinic_text

# Create the Gradio interface
with gr.Blocks(css=".gradio-container {max-width: 800px; margin: auto;}") as demo:
    gr.Markdown(
        """
        # 🏥 AI Emergency Surgery Assistant
        Enter your symptoms and optionally your city to get medical guidance and nearby clinic recommendations.
        """
    )
    
    with gr.Row():
        with gr.Column():
            symptoms = gr.Textbox(
                label="Describe your symptoms",
                placeholder="Example: I have a severe abdominal pain and vomitus for the past 2 hours...",
                lines=4
            )
            city = gr.Textbox(
                label="Your city (optional)",
                placeholder="Example: Gomel"
            )
            submit_btn = gr.Button("Get Medical Guidance", variant="primary")
    
    with gr.Row():
        with gr.Column():
            urgency = gr.Textbox(label="Urgency Classification")
            conditions = gr.Textbox(label="Possible Conditions")
            clinics = gr.Textbox(label="Nearby Clinics")
    
    submit_btn.click(
        fn=process_input,
        inputs=[symptoms, city],
        outputs=[urgency, conditions, clinics]
    )

if __name__ == "__main__":
    # Local run defaults: no public share link unless GRADIO_SHARE is set
    share_flag = os.getenv("GRADIO_SHARE", "false").lower() in ("1", "true", "yes")
    demo.launch(share=share_flag, pwa=True)
    