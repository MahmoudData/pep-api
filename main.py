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
        numero_projet = data.get('numero_projet', 'SANS_NUM')
        output_filename = f"PEP_{numero_projet}.docx"
        output_path = Path(output_filename)
        success = generate_pep_document(
            template_path=str(TEMPLATE_PATH),
            data=data,
            output_path=str(output_path)
        )
        if not success:
            raise HTTPException(status_code=500, detail="Erreur génération")
        base_url = str(request.base_url).rstrip('/')
        download_url = f"{base_url}/download/{output_filename}"
        return {
            "message": f"Document PEP généré avec succès ! Téléchargez-le ici : {download_url}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = Path(filename)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )