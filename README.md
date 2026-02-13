# 🔧 BugFixer - Analyseur d'Erreurs de Build

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Modes de fonctionnement](#modes-de-fonctionnement)
- [Installation](#installation)
- [Lancement - Mode Static (Simulation)](#lancement---mode-static-simulation)
- [Lancement - Mode Dynamic (API)](#lancement---mode-dynamic-api)
- [Flux de fonctionnement](#flux-de-fonctionnement)

---

## 🎯 Vue d'ensemble

BugFixer est un système intelligent qui analyse les erreurs de build Jenkins et les commits Git pour proposer des corrections automatiques pour les projets Spring Boot.

### Deux modes disponibles :

- **Mode Static (Simulation)** : Les données sont fournies manuellement via l'interface web
- **Mode Dynamic (API)** : Les données sont récupérées automatiquement depuis Jenkins et GitHub

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     INTERFACE WEB                                │
│                  http://localhost:8000                           │
│         (Formulaire pour logs Jenkins + commit info)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AGENT BUGFIXER                                 │
│              (FastAPI + FastMCP Client)                          │
│                                                                   │
│  bugFixerStatic.py  │  bugFixer.py                              │
│  (Mode Simulation)  │  (Mode API)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVEUR MCP                                   │
│                  (FastMCP Server)                                │
│                                                                   │
│  server-statique.py  │  server.py                               │
│  (Mode Simulation)   │  (Mode API)                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────┐           │
│  │  Tools MCP :                                      │           │
│  │  • get_jenkins_logs(build_logs)                  │           │
│  │  • get_diff_push(commit_info)                    │           │
│  │  • analyze_build_failure()                       │           │
│  └──────────────────────────────────────────────────┘           │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│  OPENROUTER API  │          │   EXTERNAL APIs  │
│      (LLM)       │          │  • Jenkins API   │
│                  │          │  • GitHub API    │
└──────────────────┘          └──────────────────┘
```

---

## 🔀 Modes de fonctionnement

### Mode Static (Simulation)
✅ Pas besoin d'API Jenkins ou GitHub  
✅ Données fournies manuellement via formulaire  
✅ Idéal pour tests et démonstrations  
✅ Aucune configuration externe requise  

### Mode Dynamic (API)
🔗 Récupération automatique depuis Jenkins  
🔗 Récupération automatique depuis GitHub  
🔗 Nécessite configuration des tokens API  
🔗 Idéal pour production  

---

## 📦 Installation

### 1️⃣ Activer l'environnement virtuel

```bash
cd /home/safwen/BugFixer
source .venv/bin/activate
```

### 2️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3️⃣ Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```bash
# Pour les deux modes
OPENROUTER_API_KEY=votre_clé_openrouter
MCP_SERVER_URL=http://localhost:8083/mcp

# Uniquement pour le Mode Dynamic
JENKINS_URL=http://votre-jenkins-url
JENKINS_USER=votre_utilisateur
JENKINS_TOKEN=votre_token
GITHUB_TOKEN=votre_token_github  # optionnel
```

---

## 🚀 Lancement - Mode Static (Simulation)

### Terminal 1 - Serveur MCP

```bash
cd /home/safwen/BugFixer
source .venv/bin/activate
cd src/mcp-server && python server-statique.py
```

**Sortie attendue :**
```
[INFO]: --- 🔧 Initialisation du serveur MCP (MODE SIMULATION) ---
[INFO]: Serveur MCP démarré sur http://localhost:8083
```

### Terminal 2 - Agent BugFixer

```bash
cd /home/safwen/BugFixer
source .venv/bin/activate
cd src/agents && python bugFixerStatic.py
```

**Sortie attendue :**
```
[INFO]: --- 🔧 Initialisation de l'API BugFixer (MODE SIMULATION) ---
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Navigateur

```
http://localhost:8000
```

### Utilisation

1. Remplir le formulaire avec :
   - Nom du job Jenkins
   - Numéro de build
   - Propriétaire du dépôt
   - Nom du dépôt
   - SHA du commit
   - **Logs Jenkins complets** (coller dans la zone de texte)
   - **Informations du commit au format JSON** (coller dans la zone de texte)

2. Cliquer sur "Analyser"

3. Obtenir les suggestions de correction

---

## 🌐 Lancement - Mode Dynamic (API)

### Terminal 1 - Serveur MCP

```bash
cd /home/safwen/BugFixer
source .venv/bin/activate
cd src/mcp-server && python server.py
```

**Sortie attendue :**
```
[INFO]: --- 🔧 Initialisation du serveur MCP (MODE API) ---
[INFO]: Serveur MCP démarré sur http://localhost:8083
```

### Terminal 2 - Agent BugFixer

```bash
cd /home/safwen/BugFixer
source .venv/bin/activate
cd src/agents && python bugFixer.py
```

**Sortie attendue :**
```
[INFO]: --- 🔧 Initialisation de l'API BugFixer (MODE API) ---
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Navigateur

```
http://localhost:8000
```

### Utilisation

1. Remplir le formulaire avec :
   - Nom du job Jenkins
   - Numéro de build
   - URL du commit GitHub

2. Cliquer sur "Analyser"

3. Le système récupère automatiquement les logs et le diff

4. Obtenir les suggestions de correction

---

## 🔄 Flux de fonctionnement

### Mode Static (Simulation)

```
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : Utilisateur remplit le formulaire                    │
│  ├─ job_name: "springboot-user-service"                         │
│  ├─ build_number: "42"                                           │
│  ├─ repo_owner: "Safwen707"                                      │
│  ├─ repo_name: "springboot-user-service"                        │
│  ├─ commit_sha: "a7f3d91"                                        │
│  ├─ build_logs: "Started by user...\n[ERROR]..."               │
│  └─ commit_info: {"sha": "...", "java_files": [...]}           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : Validation et envoi                                  │
│  ├─ Validation JSON du commit_info                              │
│  └─ POST /fix avec payload complet                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 : bugFixerStatic.py traite la requête                 │
│  ├─ Appel MCP: get_jenkins_logs(build_logs)                    │
│  │   └─ Retourne: error_lines, full_logs                       │
│  ├─ Appel MCP: get_diff_push(commit_info)                      │
│  │   └─ Retourne: diff, commit_info                            │
│  └─ Construction du prompt formaté                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 4 : Serveur MCP traite les données                      │
│  ├─ get_jenkins_logs :                                          │
│  │   ├─ Filtre les lignes d'erreur                             │
│  │   └─ Retourne erreurs + logs complets                       │
│  └─ get_diff_push :                                             │
│      ├─ Parse le commit_info fourni                            │
│      ├─ Extrait les patches                                     │
│      └─ Retourne diff formaté                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 5 : Prompt formaté construit                            │
│  🔥 ERREURS JENKINS BUILD #42                                   │
│  Job: springboot-user-service                                   │
│                                                                  │
│  [ERROR] cannot find symbol: method getUserById()              │
│  [ERROR] incompatible types: Optional<User> cannot be...       │
│                                                                  │
│  📝 COMMIT GITHUB                                               │
│  Commit: a7f3d91                                                │
│  Author: safwen707                                              │
│  Message: Add user CRUD methods                                 │
│                                                                  │
│  🔍 DIFF GIT (LIGNES MODIFIÉES)                                │
│  + User existingUser = userRepository.getUserById(1L);         │
│  + User user = userRepository.findById(userId);                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 6 : Appel OpenRouter (LLM)                              │
│  ├─ Model: meta-llama/llama-3.1-8b-instruct                    │
│  ├─ System: SYSTEM_INSTRUCTION (expert Spring Boot)            │
│  ├─ User: Prompt formaté                                        │
│  └─ max_tokens: 800, temperature: 0.1                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 7 : LLM analyse et génère la correction                 │
│                                                                  │
│  ERREUR DÉTECTÉE                                                │
│  Fichier  : UserService.java                                   │
│  Ligne    : 33                                                  │
│  Méthode  : createUser()                                        │
│                                                                  │
│  CAUSE IDENTIFIÉE                                               │
│  La méthode getUserById() n'existe pas dans UserRepository.    │
│  Spring Data JPA fournit findById() qui retourne Optional.     │
│                                                                  │
│  CODE ACTUEL                                                    │
│  + User existingUser = userRepository.getUserById(1L);         │
│                                                                  │
│  CODE CORRIGÉ                                                   │
│  User existingUser = userRepository.findById(1L)                │
│      .orElseThrow(() -> new EntityNotFoundException(...));     │
│                                                                  │
│  INSTRUCTIONS                                                   │
│  1. Ouvrir UserService.java                                    │
│  2. Aller ligne 33                                              │
│  3. Remplacer getUserById() par findById().orElseThrow()       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 8 : Affichage de la correction à l'utilisateur          │
│  └─ Interface web affiche la réponse formatée                  │
└─────────────────────────────────────────────────────────────────┘
```

### Mode Dynamic (API)

```
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : Utilisateur fournit l'URL GitHub                     │
│  ├─ job_name: "springboot-user-service"                         │
│  ├─ build_number: "42"                                           │
│  └─ commit_url: "https://github.com/owner/repo/commit/sha"     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : bugFixer.py parse l'URL et appelle MCP              │
│  ├─ Parse commit_url → extract owner, repo, sha                │
│  ├─ Appel MCP: get_jenkins_logs(job_name, build_number)        │
│  │   └─ API Jenkins récupère les logs                          │
│  └─ Appel MCP: get_diff_push(owner, repo, sha)                 │
│      └─ API GitHub récupère le diff                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 : Serveur MCP appelle les APIs externes               │
│  ├─ get_jenkins_logs :                                          │
│  │   ├─ GET {JENKINS_URL}/job/{job}/console                   │
│  │   ├─ Auth: (JENKINS_USER, JENKINS_TOKEN)                    │
│  │   └─ Filtre les erreurs                                      │
│  └─ get_diff_push :                                             │
│      ├─ GET https://api.github.com/repos/{owner}/{repo}/commits │
│      ├─ Auth: GITHUB_TOKEN (optionnel)                          │
│      └─ Parse le patch                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
                 [Suite identique au Mode Static]
                 [Étapes 4-8 : Construction prompt → LLM → Correction]
```

---

## 🔧 Dépannage

### Port déjà utilisé

```bash
# Vérifier les ports
lsof -i :8083  # MCP Server
lsof -i :8000  # BugFixer Agent

# Tuer le processus si nécessaire
kill -9 <PID>
```

### Erreur "OPENROUTER_API_KEY manquant"

Vérifier le fichier `.env` :
```bash
cat .env
# Doit contenir :
# OPENROUTER_API_KEY=votre_clé
```

### Mode Dynamic : Erreur de connexion Jenkins/GitHub

Vérifier les variables d'environnement :
```bash
# Dans .env
JENKINS_URL=http://votre-jenkins
JENKINS_USER=votre_user
JENKINS_TOKEN=votre_token
GITHUB_TOKEN=votre_token  # optionnel
```

---

## 📊 Comparaison des modes

| Aspect | Mode Static | Mode Dynamic |
|--------|-------------|--------------|
| **Configuration** | Minimale (OPENROUTER_API_KEY) | Complète (+ Jenkins + GitHub) |
| **Source des données** | Manuelle (formulaire) | Automatique (APIs) |
| **Cas d'usage** | Tests, démos, développement | Production |
| **Dépendances** | Aucune externe | Jenkins + GitHub |
| **Rapidité** | Immédiate | Dépend des APIs |
| **Reproductibilité** | Parfaite | Variable |

---

## 📝 Format des données (Mode Static)

### Logs Jenkins
```
Started by user safwen707
...
[ERROR] COMPILATION ERROR
[ERROR] /path/to/file.java:[33,46] cannot find symbol
symbol: method getUserById(java.lang.Long)
...
BUILD FAILURE
```

### Commit Info (JSON)
```json
{
  "sha": "a7f3d91",
  "author": "safwen707",
  "date": "2025-02-13T15:30:45Z",
  "message": "Add user CRUD methods",
  "java_files": [
    {
      "filename": "src/main/java/com/example/userservice/service/UserService.java",
      "status": "modified",
      "patch": "@@ -1,6 +1,7 @@\n package ...\n+import ...\n..."
    }
  ]
}
```

---

## 🎯 Prochaines étapes

1. ✅ Choisir le mode (Static ou Dynamic)
2. ✅ Installer les dépendances
3. ✅ Configurer les variables d'environnement
4. ✅ Lancer les deux serveurs
5. ✅ Tester avec des données réelles ou d'exemple

**Bon debugging ! 🚀**
# BugFixer
# BugFixer
