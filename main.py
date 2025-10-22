from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
from pep_generator import generate_pep_document

# Initialisation
app = FastAPI(title="PEP Generator API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
TEMPLATE_PATH = Path("templates/PEP_type_template.docx")


@app.get("/")
async def root():
    return {"message": "PEP Generator API", "status": "running"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "template_exists": TEMPLATE_PATH.exists()
    }


@app.post("/generate-PEP")
async def generate_pep(request: Request):
    try:
        data = await request.json()
        # Nom du fichier simple
        numero_projet = data.get('numero_projet', 'SANS_NUM')
        output_filename = f"PEP_{numero_projet}.docx"
        output_path = Path(output_filename)
        # Génération
        success = generate_pep_document(
            template_path=str(TEMPLATE_PATH),
            data=data,
            output_path=str(output_path)
        )
        if not success:
            raise HTTPException(status_code=500, detail="Erreur génération")
        # URL de téléchargement
        base_url = str(request.base_url).rstrip('/')
        return {
            "status": "success",
            "message": "Document PEP généré avec succès",
            "filename": output_filename,
            "projet": numero_projet,
            "client": data.get('client', 'N/A')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))