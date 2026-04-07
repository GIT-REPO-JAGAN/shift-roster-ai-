import pandas as pd
import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_json(text):
    """
    Extract JSON safely from LLM response
    """
    try:
        # Direct parse
        return json.loads(text)
    except:
        pass

    # Try to extract JSON block using regex
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    return None


def generate_roster(
    df,
    total_shifts,
    min_headcount,
    seniority,
    backup_rule,
    rotation,
    constraints,
    extra_rules
):
    employees = df.to_dict(orient="records")

    prompt = f"""
You are an expert workforce scheduler.

STRICT INSTRUCTIONS:
- Output ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Ensure valid syntax

INPUT:
Employees: {employees}

RULES:
- Total shifts per day: {total_shifts}
- Minimum headcount per shift: {min_headcount}
- Seniority classification: {seniority}
- Backup rule: {backup_rule}
- Rotation: {rotation}
- Constraints: {constraints}
- Additional rules: {extra_rules}

OUTPUT FORMAT:
[
  {{
    "Name": "Employee Name",
    "Mon": "Morning",
    "Tue": "Afternoon",
    "Wed": "Night",
    "Thu": "OFF",
    "Fri": "Morning",
    "Sat": "OFF",
    "Sun": "Night"
  }}
]
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2  # more stable output
        )

        result_text = response.choices[0].message.content.strip()

        # Extract JSON safely
        data = extract_json(result_text)

        if data:
            df_output = pd.DataFrame(data)

            # Ensure column order
            expected_cols = ["Name", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            df_output = df_output.reindex(columns=expected_cols)

            return df_output

        else:
            return pd.DataFrame({
                "Error": ["Failed to parse AI output"],
                "Raw Output": [result_text]
            })

    except Exception as e:
        return pd.DataFrame({
            "Error": ["Exception occurred"],
            "Details": [str(e)]
        })
