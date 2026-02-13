# 🚨 Erreur 401 : Clé API OpenRouter Invalide

## Le problème

L'erreur `401: {"error":{"message":"User not found.","code":401}}` provient de l'API OpenRouter.

Cela signifie que votre clé API `OPENROUTER_API_KEY` est :
- ❌ Invalide
- ❌ Expirée
- ❌ Associée à un compte qui n'existe plus
- ❌ Mal formatée

## ✅ Solution : Obtenir une nouvelle clé API

### Étape 1 : Créer un compte OpenRouter (si nécessaire)

1. Allez sur : https://openrouter.ai/
2. Cliquez sur "Sign In" ou "Sign Up"
3. Créez un compte ou connectez-vous

### Étape 2 : Obtenir une clé API

1. Allez sur : https://openrouter.ai/keys
2. Cliquez sur "Create Key"
3. Donnez un nom à votre clé (ex: "BugFixer")
4. Copiez la clé générée (format: `sk-or-v1-...`)

### Étape 3 : Mettre à jour le fichier .env

```bash
cd /home/safwen/BugFixer
nano .env
```

Remplacez la ligne :
```
OPENROUTER_API_KEY=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
```

Par votre nouvelle clé :
```
OPENROUTER_API_KEY=sk-or-v1-VOTRE_NOUVELLE_CLE_ICI
```

Sauvegardez avec `Ctrl+O`, puis `Enter`, puis `Ctrl+X`

### Étape 4 : Redémarrer l'agent BugFixer

Dans le **Terminal 2** :
1. Arrêtez l'agent : `Ctrl+C`
2. Relancez-le :
```bash
cd /home/safwen/BugFixer
source .venv/bin/activate
cd src/agents && python bugFixerStatic.py
```

### Étape 5 : Retester

Retournez sur http://localhost:8000 et réessayez votre analyse.

---

## 💰 Note sur les crédits

OpenRouter nécessite des crédits pour fonctionner :
- Nouveaux comptes : généralement $5 de crédits gratuits
- Vérifiez votre solde sur : https://openrouter.ai/credits

Si vous n'avez plus de crédits, vous devrez en acheter.

---

## 🔄 Alternative : Utiliser une autre API LLM

Si vous ne souhaitez pas utiliser OpenRouter, vous pouvez modifier le code pour utiliser :
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Google (Gemini)
- Ollama (local, gratuit)

---

## 🧪 Tester la clé API manuellement

Pour vérifier si votre clé fonctionne :

```bash
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer sk-or-v1-VOTRE_CLE_ICI"
```

Si la clé est valide, vous verrez vos informations de compte.
Si invalide, vous verrez l'erreur 401.

---

## ✅ Checklist

- [ ] Obtenir une nouvelle clé API sur https://openrouter.ai/keys
- [ ] Mettre à jour le fichier `.env`
- [ ] Redémarrer l'agent BugFixer (Terminal 2)
- [ ] Vérifier que vous avez des crédits
- [ ] Retester l'application

---

**La clé actuelle dans votre .env est invalide et doit être remplacée !**
