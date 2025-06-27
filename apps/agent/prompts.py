def build_antibiotic_prompt(ctx: dict) -> str:
    return (
        f"The patient has sepsis. Identified organism: {ctx.get('organism')}. "
        f"Susceptibility: {ctx.get('sensitivity')}. "
        f"Current antibiotics: {', '.join(ctx.get('antibiotics', [])) or 'none'}. "
        "According to the sepsis protocol, what antibiotic should be used?"
    )


def build_next_step_prompt(ctx: dict) -> str:
    return (
        f"Patient with sepsis. Clinical condition: {ctx.get('clinical_status')}. "
        f"Recent events: {ctx.get('events')}. "
        "What is the next recommended step in treatment, according to the current sepsis protocol?"
    )


def build_ccih_prompt(ctx: dict) -> str:
    return (
        f"Patient background includes: {ctx.get('comorbidities')}. "
        f"Identified organism: {ctx.get('organism')}. "
        f"Previously used antibiotics: {', '.join(ctx.get('previous_antibiotics', [])) or 'none'}. "
        "Are there any additional infection control recommendations based on the institutional protocol?"
    )
