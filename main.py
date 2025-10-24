from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pep_generator import generate_pep_document
import time

app = FastAPI(title="PEP Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def cleanup_file(file_path: Path, delay: int = 60):
    """Supprime le fichier après un délai"""
    time.sleep(delay)
    if file_path.exists():
        file_path.unlink()


@app.post("/generate-PEP")
async def generate_pep(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        numero_projet = data.get('numero_projet', 'SANS_NUM')
        
        # Créer un dossier temporaire
        output_dir = Path("generated_files")
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"PEP_{numero_projet}.docx"
        output_path = output_dir / output_filename
        
        # Générer le document
        success = generate_pep_document(
            template_path=str(TEMPLATE_PATH),
            data=data,
            output_path=str(output_path)
        )
        
        if not success or not output_path.exists():
            raise HTTPException(status_code=500, detail="Erreur génération")
        
        # Nettoyer le fichier après envoi
        background_tasks.add_task(cleanup_file, output_path)
        
        # Retourner le fichier directement
        return FileResponse(
            path=str(output_path),
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

