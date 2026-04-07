from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
from roster_engine import generate_roster

app = FastAPI()

# ✅ FIXED: directory should be string (not dict)
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
    try:
        print("📥 File received:", file.filename)

        # Read Excel
        df = pd.read_excel(file.file)
        print("📊 Columns:", df.columns.tolist())

        # Validate Excel
        if "Name" not in df.columns:
            df.columns = [col.strip() for col in df.columns]
            if "Name" not in df.columns:
                return JSONResponse(content={
                    "error": "Excel must contain 'Name' column",
                    "columns_found": df.columns.tolist()
                })

        # Generate roster
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

        # Save file
        output_file = "generated_roster.xlsx"

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            roster_df.to_excel(writer, index=False, sheet_name="Roster")

        print("✅ File saved:", output_file)

        # Ensure file exists before returning
        if os.path.exists(output_file):
            return FileResponse(
                path=output_file,
                filename="Shift_Roster.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            return JSONResponse(content={"error": "File not generated"})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return JSONResponse(content={
            "error": "Internal Server Error",
            "details": str(e)
        })
