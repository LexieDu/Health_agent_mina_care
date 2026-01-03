def local_otc_mapping(user_input: str) -> dict:
    """
    Local symptom → OTC candidate mapping.
    Returns dict with: medicines (list), self_care (list), red_flags (list)
    """
    text = (user_input or "").lower()

    def has(*kw):
        return any(k in text for k in kw)

    medicines = []
    self_care = []
    red_flags = []

    # Fever / flu aches
    if has("fever", "temperature", "chills"):
        medicines += [
            {"name": "acetaminophen", "purpose": "reduce fever and aches"},
            {"name": "ibuprofen", "purpose": "reduce fever, aches, inflammation"},
        ]
        self_care += [
            "Drink fluids regularly (water, soup, oral rehydration).",
            "Rest and avoid intense activity.",
            "Check temperature every 4–6 hours.",
        ]
        red_flags += [
            "Fever ≥ 103°F (39.4°C) or lasting > 3 days.",
            "Trouble breathing, chest pain, confusion, severe weakness.",
            "Severe dehydration (very dark urine, dizziness, fainting).",
        ]

    # Cold / congestion
    if has("congestion", "stuffy", "blocked nose", "sinus", "runny nose", "sneeze", "cold"):
        medicines += [
            {"name": "pseudoephedrine", "purpose": "relieve nasal congestion"},
            {"name": "oxymetazoline nasal spray", "purpose": "short-term nasal decongestion (≤3 days)"},
            {"name": "cetirizine", "purpose": "reduce runny nose/sneezing (allergy-like symptoms)"},
        ]
        self_care += [
            "Use saline spray / rinse to clear congestion.",
            "Humidifier or warm shower steam 10–15 min.",
            "Honey/lemon warm water for throat comfort (not for children <1).",
        ]
        red_flags += [
            "Shortness of breath or wheezing.",
            "Severe sinus pain with high fever.",
            "Symptoms worsening after 7–10 days.",
        ]

    # Cough
    if has("cough", "coughing"):
        if has("phlegm", "mucus", "productive"):
            medicines += [{"name": "guaifenesin", "purpose": "loosen mucus (wet cough)"}]
        else:
            medicines += [{"name": "dextromethorphan", "purpose": "suppress dry cough"}]
        self_care += [
            "Sip warm fluids; try honey (if age-appropriate).",
            "Avoid smoke and strong fragrances.",
        ]
        red_flags += [
            "Coughing blood or severe shortness of breath.",
            "High fever + worsening cough.",
            "Cough lasting > 3 weeks.",
        ]

    # Sore throat
    if has("sore throat", "throat pain", "tonsil"):
        medicines += [{"name": "benzocaine lozenges/spray", "purpose": "temporary throat numbing"}]
        self_care += [
            "Gargle warm salt water 3–4x/day.",
            "Lozenges/warm tea for comfort.",
        ]
        red_flags += [
            "Trouble swallowing saliva or breathing.",
            "Severe throat pain with high fever.",
            "Rash + sore throat (possible strep/scarlet fever).",
        ]

    # Heartburn / reflux
    if has("heartburn", "acid reflux", "reflux", "burning chest"):
        medicines += [
            {"name": "famotidine", "purpose": "reduce stomach acid (H2 blocker)"},
            {"name": "calcium carbonate", "purpose": "fast antacid relief"},
        ]
        self_care += [
            "Avoid late meals; wait 2–3 hours before lying down.",
            "Avoid trigger foods (spicy, fatty, alcohol, coffee).",
        ]
        red_flags += [
            "Chest pain that spreads to arm/jaw or with sweating (urgent).",
            "Black/tarry stools or vomiting blood.",
            "Unintentional weight loss or trouble swallowing.",
        ]

    # Diarrhea
    if has("diarrhea", "loose stool"):
        medicines += [
            {"name": "oral rehydration salts", "purpose": "prevent dehydration"},
            {"name": "loperamide", "purpose": "reduce diarrhea frequency (if no fever/blood)"},
        ]
        self_care += [
            "Oral rehydration solution; small sips frequently.",
            "Eat bland foods (bananas, rice, toast) if tolerated.",
        ]
        red_flags += [
            "Bloody stool or high fever.",
            "Signs of dehydration (dizziness, very low urination).",
            "Severe abdominal pain or symptoms > 2–3 days.",
        ]

    # Allergies
    if has("allergy", "hives", "itchy", "sneezing", "watery eyes"):
        medicines += [
            {"name": "cetirizine", "purpose": "allergy relief (less drowsy)"},
            {"name": "loratadine", "purpose": "allergy relief (less drowsy)"},
            {"name": "diphenhydramine", "purpose": "allergy relief (more drowsy)"},
        ]
        self_care += [
            "Rinse face/hands after outdoor exposure; shower before bed.",
            "Use a HEPA filter if symptoms are frequent indoors.",
        ]
        red_flags += [
            "Lip/tongue swelling or trouble breathing (emergency).",
            "Widespread hives with vomiting/dizziness (emergency).",
            "Severe eye pain or vision changes.",
        ]

    # If nothing matched, keep it minimal (don’t force NSAIDs)
    if not medicines:
        medicines = [{"name": "acetaminophen", "purpose": "pain/fever relief (only if relevant)"}]
        self_care = ["Rest, hydrate, and monitor symptoms."]
        red_flags = ["If symptoms are severe, worsening, or unusual, seek medical care."]

    # Deduplicate by name
    seen = set()
    uniq_meds = []
    for m in medicines:
        key = (m.get("name") or "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            uniq_meds.append(m)

    return {"medicines": uniq_meds[:5], "self_care": self_care[:6], "red_flags": red_flags[:5]}
