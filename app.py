from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import pandas as pd
import os
from roster_engine import generate_roster

app = FastAPI()


# ✅ Home Page (NO Jinja → No Errors)
@app.get("/", response_class=HTMLResponse)
def form_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shift Roster Generator</title>
        <style>
            body {
                font-family: Arial;
                padding: 40px;
                background-color: #f4f6f8;
            }
            form {
                background: white;
                padding: 20px;
                border-radius: 10px;
                width: 400px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            }
            input, button {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
            }
            button {
                background-color: green;
                color: white;
                font-weight: bold;
            }
        </style>
    </head>
    <body>

        <h2>Shift Roster Generator</h2>

        <form action="/generate/" method="post" enctype="multipart/form-data">

            <label>Upload Excel:</label>
            <input type="file" name="file" required>

            <input type="number" name="total_shifts" placeholder="Total shifts per day" required>
            <input type="number" name="min_headcount" placeholder="Min headcount per shift" required>

            <input type="text" name="seniority" placeholder="Seniority classification">
            <input type="text" name="backup_rule" placeholder="Backup rule">
            <input type="text" name="rotation" placeholder="Rotation frequency">
            <input type="text" name="constraints" placeholder="Constraints">
            <input type="text" name="extra_rules" placeholder="Additional rules">

            <button type="submit">Generate Roster</button>

        </form>

    </body>
    </html>
    """


# ✅ Generate Roster API
@app.post("/generate/")
async def generate(
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

        print("✅ File saved")

        return FileResponse(
            path=output_file,
            filename="Shift_Roster.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        print("❌ ERROR:", str(e))
        return JSONResponse(content={
            "error": "Internal Server Error",
            "details": str(e)
        })
