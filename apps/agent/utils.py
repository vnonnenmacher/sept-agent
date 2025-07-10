import json
import re


def clean_json_output(text: str):
    """
    Clean LLM output to ensure it's a valid JSON list of objects.
    Wraps multiple top-level objects in brackets if needed.
    Removes code block markers like ```json or ```python.
    """
    # Remove ```json or ```python or ``` lines
    text = re.sub(r"^```(json|python)?\\n?", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text.strip())

    # Trim whitespace and make sure it starts with [ or {
    text = text.strip()

    # Heuristics: if the response looks like multiple objects but not inside a list
    if text.startswith("{") and text.count("}") > 1 and not text.startswith("["):
        text = f"[{text}]"

    # Try parsing
    return json.loads(text)
