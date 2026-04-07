import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_roster(df, total_shifts, min_headcount, seniority, backup_rule, rotation, constraints, extra_rules):

    employees = df.to_dict(orient="records")

    prompt = f"""
You are an expert workforce scheduler.

Create a STRICT JSON output.

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

OUTPUT FORMAT (STRICT JSON):
[
  {{
    "Name": "Employee Name",
    "Mon": "Morning",
    "Tue": "Night",
    "Wed": "OFF",
    "Thu": "Afternoon",
    "Fri": "Morning",
    "Sat": "OFF",
    "Sun": "Night"
  }}
]

ONLY RETURN JSON. NO EXTRA TEXT.
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.choices[0].message.content

    try:
        data = eval(result_text)  # quick parse (can improve later)
        return pd.DataFrame(data)
    except:
        return pd.DataFrame({"Raw Output": [result_text]})
