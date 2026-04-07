import pandas as pd
import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_json(text):
    """
    Extract JSON safely from LLM response
    """
    try:
        return json.loads(text)
    except:
        pass

    # Try extracting JSON array using regex
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
    try:
        # Convert dataframe to records
        employees = df.to_dict(orient="records")

        print("INPUT EMPLOYEES:", employees)

        prompt = f"""
You are an expert workforce scheduler.

STRICT RULES:
- Output ONLY valid JSON
- No explanation, no markdown
- Use EXACT shift names: Morning, Afternoon, Night, OFF
- Each employee must have exactly 2 OFF days
- No more than 2 consecutive Night shifts
- Ensure fair distribution

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

        # Call Groq API
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        result_text = response.choices[0].message.content.strip()

        print("RAW AI OUTPUT:", result_text)  # Debug log

        # Extract JSON safely
        data = extract_json(result_text)

        if data and isinstance(data, list):
            df_output = pd.DataFrame(data)

            # Ensure correct column order
            expected_cols = ["Name", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            df_output = df_output.reindex(columns=expected_cols)

            print("SUCCESS: Roster generated")

            return df_output

        else:
            print("ERROR: AI output not valid JSON")

            return pd.DataFrame({
                "Error": ["AI output not valid JSON"],
                "Raw Output": [result_text]
            })

    except Exception as e:
        print("EXCEPTION:", str(e))

        return pd.DataFrame({
            "Error": ["Exception occurred"],
            "Details": [str(e)]
        })
