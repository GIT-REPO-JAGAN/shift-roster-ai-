# Shift Roster AI (Groq Powered)

Upload employee Excel → Define rules → Generate AI-based shift roster.

## Setup

1. Clone repo
2. Add `.env` file with GROQ_API_KEY
3. Install dependencies:
   pip install -r requirements.txt
4. Run:
   uvicorn app:app --reload

## Tech Stack
- FastAPI
- Groq (LLM)
- Pandas
