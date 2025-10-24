from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import smtplib
import os


# Configuration email via variables d'environnement
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp-mail.outlook.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")  
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  

def send_email_smtp(recipient: str, subject: str, body: str, attachment_path: Path):
    """
    Envoie un email via SMTP (compatible Outlook/Office365) avec une pièce jointe
    
    Args:
        recipient: Adresse email du destinataire
        subject: Sujet de l'email
        body: Corps de l'email
        attachment_path: Chemin vers le fichier à attacher
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    try:
        if not SMTP_EMAIL or not SMTP_PASSWORD:
            raise Exception("Configuration SMTP manquante (SMTP_EMAIL ou SMTP_PASSWORD)")
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Ajouter le corps du message
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Attacher le fichier
        if attachment_path.exists():
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment_path.name}'
                )
                msg.attach(part)
        
        # Connexion au serveur SMTP et envoi
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Sécuriser la connexion
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False