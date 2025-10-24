from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pep_generator import generate_pep_document
from email_service import send_email_smtp
from utilis import cleanup_file
import os


app = FastAPI(title="PEP Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATE_PATH = Path("templates/PEP_type_template.docx")

# Configuration email via variables d'environnement
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp-mail.outlook.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")  # Votre email Outlook
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Mot de passe ou App Password


@app.get("/")
async def root():
    return {"message": "PEP Generator API", "status": "running"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "template_exists": TEMPLATE_PATH.exists(),
        "smtp_configured": bool(SMTP_EMAIL and SMTP_PASSWORD)
    }


@app.post("/generate-PEP")
async def generate_pep(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        
        # Récupérer les informations nécessaires
        numero_projet = data.get('numero_projet', 'SANS_NUM')
        recipient_email = data.get('email_destinataire')
        
        # Vérifier que l'email destinataire est fourni
        if not recipient_email:
            raise HTTPException(
                status_code=400, 
                detail="L'adresse email du destinataire est obligatoire (email_destinataire)"
            )
        
        # Vérifier la configuration SMTP
        if not SMTP_EMAIL or not SMTP_PASSWORD:
            raise HTTPException(
                status_code=500,
                detail="Configuration SMTP manquante sur le serveur"
            )
        
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
        
        # Préparer le contenu de l'email
        email_subject = f"PEP - Projet {numero_projet}"
        email_body = f"""Bonjour,

Veuillez trouver ci-joint le document PEP pour le projet {numero_projet}.

Ce document a été généré automatiquement.

Cordialement,
Système de génération PEP
"""
        
        # Envoyer l'email
        email_sent = send_email_smtp(
            recipient=recipient_email,
            subject=email_subject,
            body=email_body,
            attachment_path=output_path
        )
        
        if not email_sent:
            raise HTTPException(
                status_code=500, 
                detail="Erreur lors de l'envoi de l'email"
            )
        
        # Nettoyer le fichier après l'envoi
        background_tasks.add_task(cleanup_file, output_path, delay=10)
        
        # Retourner une confirmation
        return {
            "success": True,
            "message": f"Document PEP généré et envoyé à {recipient_email}",
            "projet": numero_projet,
            "filename": output_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

