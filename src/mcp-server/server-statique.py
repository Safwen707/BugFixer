import logging
import os
import asyncio
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(dotenv_path="../.env")

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Error Fixer MCP Server 🔧")


# ─────────────────────────────────────────
# TOOL 1 : Récupérer les logs Jenkins
# ─────────────────────────────────────────
@mcp.tool()
def get_jenkins_logs(
        build_number: str,
        job_name: str,
) -> dict:
    """Récupère les logs d'un build Jenkins échoué.

    Args:
        build_number: Numéro du build Jenkins échoué (ex: "42").
        job_name: Nom du job Jenkins (ex: "springboot-user-service").

    Returns:
        Un dictionnaire contenant les lignes d'erreur du build ou un message d'erreur.
    """
    logger.info(f"--- 🛠️ Tool: get_jenkins_logs | job={job_name} | build={build_number} ---")

    jenkins_url   = os.getenv("JENKINS_URL")
    jenkins_user  = os.getenv("JENKINS_USER")
    jenkins_token = os.getenv("JENKINS_TOKEN")

    try:
        url = f"{jenkins_url}/job/{job_name}/{build_number}/consoleText"

        response = httpx.get(
            url,
            auth=(jenkins_user, jenkins_token),
        )
        response.raise_for_status()

        logs = response.text

        # Filtrer uniquement les lignes d'erreur pertinentes
        error_lines = [
            line for line in logs.splitlines()
            if any(keyword in line for keyword in
                   ["ERROR", "FAILED", "Exception", "error", "BUILD FAILURE"])
        ]

        logger.info(f"✅ {len(error_lines)} lignes d'erreur détectées")

        return {
            "job_name"    : job_name,
            "build_number": build_number,
            "error_lines" : error_lines,
            "status"      : "retrieved"
        }

    except httpx.HTTPError as e:
        return {"error": f"Impossible de récupérer les logs Jenkins : {e}"}


# ─────────────────────────────────────────
# TOOL 2 : Récupérer le diff du push Git
# VERSION AVEC CHUNKING : Divise les patches en tranches
# ─────────────────────────────────────────
MAX_CHARS_PER_CHUNK = 800  # ~200 tokens par chunk

@mcp.tool()
def get_diff_push(
        repo_owner: str,
        repo_name : str,
        commit_sha: str,
        chunk_index: int = 0,  # Index du chunk demandé (0 = premier)
) -> dict:
    """Récupère les lignes modifiées d'un commit, divisées en chunks.

    Si le diff est trop grand, il sera divisé en plusieurs chunks.
    Appelez avec chunk_index=0, puis chunk_index=1, etc. jusqu'à is_last=True.

    Args:
        repo_owner: Propriétaire du dépôt GitHub.
        repo_name : Nom du dépôt GitHub.
        commit_sha: Hash du commit.
        chunk_index: Index du chunk à récupérer (défaut: 0).

    Returns:
        Dictionnaire avec le chunk de diff, l'index, et si c'est le dernier.
    """
    logger.info(f"--- 🛠️ Tool: get_diff_push | {repo_owner}/{repo_name}@{commit_sha[:7]} | chunk={chunk_index} ---")

    try:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{commit_sha}"
        response = httpx.get(url, headers={"Accept": "application/vnd.github.v3+json"})
        response.raise_for_status()
        data = response.json()

        # Construire le diff complet (lignes +/- uniquement)
        all_lines = []
        for f in data.get("files", []):
            patch = f.get("patch", "")
            if patch:
                filename = f["filename"].split('/')[-1]
                lines = [
                    line for line in patch.split('\n')
                    if (line.startswith('+') or line.startswith('-'))
                       and not line.startswith('+++')
                       and not line.startswith('---')
                ]
                if lines:
                    all_lines.append(f"[{filename}]")
                    all_lines.extend(lines[:15])  # Max 15 lignes par fichier

        full_diff = '\n'.join(all_lines)

        # Diviser en chunks
        chunks = []
        current_chunk = ""
        for line in full_diff.split('\n'):
            if len(current_chunk) + len(line) + 1 > MAX_CHARS_PER_CHUNK:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += ('\n' + line if current_chunk else line)
        if current_chunk:
            chunks.append(current_chunk)

        # Si pas de chunks, retourner vide
        if not chunks:
            return {"diff": "", "chunk": 0, "total": 0, "is_last": True, "status": "retrieved"}

        # Retourner le chunk demandé
        total_chunks = len(chunks)
        if chunk_index >= total_chunks:
            chunk_index = total_chunks - 1

        logger.info(f"✅ Chunk {chunk_index + 1}/{total_chunks} ({len(chunks[chunk_index])} chars)")

        return {
            "diff": chunks[chunk_index],
            "chunk": chunk_index,
            "total": total_chunks,
            "is_last": chunk_index >= total_chunks - 1,
            "status": "retrieved"
        }

    except httpx.HTTPError as e:
        return {"error": str(e)}


# ─────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"🚀 Error Fixer MCP Server démarré sur le port {os.getenv('PORT', 8083)}")
    asyncio.run(
        mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8083)),
        )
    )

