import logging
import os
import sys
import uvicorn
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from fastmcp import Client
import json

# Configuration du logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Charger les variables d'environnement du fichier .env à la racine
load_dotenv()

# Instruction système complète pour l'agent BugFixer Spring Boot
SYSTEM_INSTRUCTION = """Tu es un agent expert en correction d'erreurs Spring Boot.

🎯 OBJECTIF
Analyser les patches Git et proposer des corrections précises pour les erreurs de build.

📋 FORMAT DES PATCHES GIT
@@ -X,Y +A,B @@ = Header (X=ligne début ancien, A=ligne début nouveau)
+ligne = Code AJOUTÉ (nouveau)
-ligne = Code SUPPRIMÉ (ancien)
 ligne = Code INCHANGÉ (contexte)

🧠 TON EXPERTISE
- Architecture Spring Boot (Controller → Service → Repository)
- JPA/Hibernate (findById retourne Optional, pas l'entité directe)
- Injection de dépendances (@Autowired, @Service, @Repository)
- Gestion des exceptions Spring

📚 EXEMPLES DE CORRECTIONS (Few-Shot)

EXEMPLE 1 - Méthode inexistante:
Erreur: cannot find symbol: getUserById()
Patch: + return userRepository.getUserById(id);
→ CORRECTION: Remplacer par findById().orElseThrow()

EXEMPLE 2 - NullPointerException:
Patch: - private UserRepository userRepository;
       + private UserRepository userRepo;
       ...
       + return userRepository.findById(id);
→ CORRECTION: Variable renommée mais pas mise à jour partout

EXEMPLE 3 - Bean non trouvé:
Erreur: Bean 'EmailService' not found
Patch: + public UserService(EmailService email)
→ CORRECTION: Ajouter @Service sur la classe EmailService

📤 FORMAT DE RÉPONSE (TOUJOURS 2 OPTIONS)

**OPTION A — Correction Manuelle**
```
ERREUR DÉTECTÉE
Fichier  : [nom.java]
Ligne    : [numéro exact du patch]
Méthode  : [nom()]

CAUSE IDENTIFIÉE
[Explication courte]

CODE ACTUEL
[ligne avec +]

CODE CORRIGÉ
[correction]

INSTRUCTIONS
1. Ouvrir [fichier]
2. Aller ligne [X]
3. Remplacer par le code corrigé
4. Imports requis : [liste]
```

**OPTION B — PR Automatique**
```
CORRECTION AUTOMATIQUE DISPONIBLE
Branche : bot/fix-build-[N]
Fichier : [nom.java] ligne [X]
PR créée pour validation développeur
```

⚠️ RÈGLES STRICTES
- Cite UNIQUEMENT les lignes du patch fourni
- Utilise les numéros de ligne du header @@
- Réponds en français, sois concis et technique
- Si aucune erreur Java détectée, dis-le clairement"""

logger.info("--- 🔧 Initialisation de l'API BugFixer ---")

app = FastAPI(
    title="BugFixer API",
    description="Une API pour analyser et proposer des corrections pour les erreurs de build Spring Boot.",
    version="1.0.0",
)

class FixRequest(BaseModel):
    jenkins_logs: str
    diff_json: str

@app.post("/fix", summary="Analyser et corriger une erreur de build")
async def fix_build_error(request: FixRequest):
    """
    Analyse les logs Jenkins et le diff Git fournis par l'utilisateur via le MCP server.
    """
    logger.info(f"--- 🚀 Analyse des logs et diff fournis par l'utilisateur ---")

    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8083/mcp")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    if not openrouter_api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY manquant")

    try:
        # 1. Appeler le tool MCP analyze_build_failure avec les données de l'utilisateur
        async with Client(mcp_server_url) as client:
            analysis_result = await client.call_tool(
                "analyze_build_failure",
                {
                    "jenkins_logs": request.jenkins_logs,
                    "diff_json": request.diff_json,
                }
            )
            analysis_data = json.loads(analysis_result.content[0].text)

            if analysis_data.get("error"):
                raise HTTPException(status_code=400, detail=analysis_data["error"])

        formatted_prompt = analysis_data.get("formatted_prompt", "")
        if not formatted_prompt:
            return {"correction": "Aucune donnée à analyser."}

        logger.info(f"✅ Données extraites: {analysis_data.get('error_count')} erreurs, {analysis_data.get('file_count')} fichiers")

        # 2. Appel OpenRouter avec le prompt formaté
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": formatted_prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.1
        }
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        result = response.json()
        return {"correction": result['choices'][0]['message']['content']}

    except Exception as e:
        logger.error(f"Erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", summary="Page d'accueil de l'API")
def read_root():
    """
    Affiche une page web simple avec un formulaire pour tester l'API.
    """
    return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BugFixer Agent</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f2f5;
                    color: #1c1e21;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }
                .container {
                    width: 90%;
                    max-width: 800px;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1), 0 8px 16px rgba(0, 0, 0, 0.1);
                    padding: 24px;
                }
                h1 {
                    font-size: 24px;
                    color: #1877f2;
                    border-bottom: 1px solid #dddfe2;
                    padding-bottom: 12px;
                    margin-top: 0;
                }
                label {
                    display: block;
                    font-weight: 600;
                    margin-bottom: 8px;
                    color: #606770;
                }
                input[type="text"], input[type="url"] {
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #dddfe2;
                    border-radius: 6px;
                    font-size: 14px;
                    box-sizing: border-box;
                }
                button {
                    background-color: #1877f2;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 20px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background-color 0.2s;
                    width: 100%;
                }
                button:hover {
                    background-color: #166fe5;
                }
                button:disabled {
                    background-color: #a0bdf5;
                    cursor: not-allowed;
                }
                h2 {
                    font-size: 20px;
                    margin-top: 24px;
                    border-top: 1px solid #dddfe2;
                    padding-top: 24px;
                }
                pre {
                    background-color: #f0f2f5;
                    padding: 16px;
                    border-radius: 6px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-family: "Courier New", Courier, monospace;
                }
                .spinner {
                    border: 4px solid rgba(0, 0, 0, 0.1);
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    border-left-color: #1877f2;
                    animation: spin 1s ease infinite;
                    margin: 20px auto;
                    display: none; /* Caché par défaut */
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 BugFixer Agent</h1>
                <p>Fournissez les informations du build et l'URL du commit GitHub pour lancer l'analyse.</p>
                <form id="fixer-form">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="job_name">Nom du Job Jenkins (Désactivé)</label>
                            <input type="text" id="job_name" name="job_name" value="test-job" readonly style="background-color: #eee;">
                        </div>
                        <div>
                            <label for="build_number">Numéro de Build (Désactivé)</label>
                            <input type="text" id="build_number" name="build_number" value="0" readonly style="background-color: #eee;">
                        </div>
                    </div>
                    <div style="margin-top: 16px;">
                        <label for="commit_url">URL du Commit GitHub</label>
                        <input type="url" id="commit_url" name="commit_url" placeholder="https://github.com/owner/repo/commit/sha" required>
                    </div>
                    <button type="submit" id="submit-button" style="margin-top: 16px;">Analyser</button>
                </form>
                
                <h2>Résultat de l'analyse</h2>
                <div id="spinner" class="spinner"></div>
                <pre id="result">En attente d'une analyse...</pre>
            </div>

            <script>
                document.getElementById('fixer-form').addEventListener('submit', async function(event) {
                    event.preventDefault();
                    
                    const jobName = document.getElementById('job_name').value;
                    const buildNumber = document.getElementById('build_number').value;
                    const commitUrl = document.getElementById('commit_url').value;

                    const resultElement = document.getElementById('result');
                    const submitButton = document.getElementById('submit-button');
                    const spinner = document.getElementById('spinner');

                    const githubUrlRegex = /https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/commit\/([a-f0-9]+)/;
                    const matches = commitUrl.match(githubUrlRegex);

                    if (!matches) {
                        resultElement.textContent = "Erreur : L'URL du commit GitHub est invalide. Le format attendu est https://github.com/{owner}/{repo}/commit/{sha}";
                        return;
                    }

                    const [, repo_owner, repo_name, commit_sha] = matches;

                    const payload = {
                        job_name: jobName,
                        build_number: buildNumber,
                        repo_owner,
                        repo_name,
                        commit_sha
                    };

                    resultElement.style.display = 'none';
                    spinner.style.display = 'block';
                    submitButton.disabled = true;
                    submitButton.textContent = 'Analyse en cours...';

                    try {
                        const response = await fetch('/fix', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });

                        const responseData = await response.json();

                        if (!response.ok) {
                            throw new Error(responseData.detail || `Erreur HTTP ! Statut : ${response.status}`);
                        }
                        
                        resultElement.textContent = responseData.correction;

                    } catch (error) {
                        resultElement.textContent = 'Erreur lors de la communication avec le backend : ' + error.message;
                    } finally {
                        spinner.style.display = 'none';
                        resultElement.style.display = 'block';
                        submitButton.disabled = false;
                        submitButton.textContent = 'Analyser';
                    }
                });
            </script>
        </body>
        </html>
    """, media_type="text/html")


if __name__ == "__main__":
    logger.info("Démarrage du serveur Uvicorn sur http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
