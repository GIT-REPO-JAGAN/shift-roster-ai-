from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from roster_engine import generate_roster

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate/")
async def generate(
    request: Request,
    file: UploadFile = File(...),
    total_shifts: int = Form(...),
    min_headcount: int = Form(...),
    seniority: str = Form(...),
    backup_rule: str = Form(...),
    rotation: str = Form(...),
    constraints: str = Form(...),
    extra_rules: str = Form(...)
):
    df = pd.read_excel(file.file)

    roster_df = generate_roster(
        df,
        total_shifts,
        min_headcount,
        seniority,
        backup_rule,
        rotation,
        constraints,
        extra_rules
    )

    output_file = "generated_roster.xlsx"
    roster_df.to_excel(output_file, index=False)

    return FileResponse(output_file, filename="Shift_Roster.xlsx")
