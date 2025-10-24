from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pep_generator import generate_pep_document
import base64
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
            raise HTTPException(status_code=500, detail="Erreur lors de la génération du document")
        
        # Lire le fichier et le convertir en base64
        with open(output_path, "rb") as f:
            file_content = f.read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Nettoyer le fichier après
        background_tasks.add_task(cleanup_file, output_path)
        
        # Retourner le fichier en base64 dans du JSON
        return {
            "success": True,
            "message": f"Document PEP '{output_filename}' généré avec succès !",
            "filename": output_filename,
            "file_base64": file_base64,
            "numero_projet": numero_projet
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Endpoint de téléchargement direct si besoin"""
    output_dir = Path("generated_files")
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )