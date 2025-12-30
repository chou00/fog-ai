# 🚀 Instructions Rapides - Push sur Git

## ✅ État actuel

Le dépôt Git est **déjà initialisé** et **tous les fichiers sont commités** !

```
✅ Git repository initialisé
✅ 18 fichiers commités
✅ Prêt à être poussé sur GitHub/GitLab
```

## 📤 Option 1: Utiliser le script automatique (Windows)

```powershell
cd fog-ai-anomaly-detection
.\push_to_github.ps1
```

Le script vous guidera pour:
- Ajouter votre dépôt GitHub
- Pousser le code automatiquement

## 📤 Option 2: Commandes manuelles

### Étape 1: Créer un dépôt sur GitHub

1. Allez sur https://github.com/new
2. Nom: `fog-ai-anomaly-detection`
3. **Ne cochez PAS** "Initialize with README"
4. Cliquez "Create repository"

### Étape 2: Connecter et pousser

```powershell
cd fog-ai-anomaly-detection

# Ajouter le remote (remplacez USERNAME)
git remote add origin https://github.com/USERNAME/fog-ai-anomaly-detection.git

# Renommer la branche en main
git branch -M main

# Pousser le code
git push -u origin main
```

## 📥 Sur Kali Linux - Récupérer le projet

Une fois poussé sur GitHub:

```bash
# Installer Git (si nécessaire)
sudo apt-get update
sudo apt-get install -y git

# Cloner le dépôt
git clone https://github.com/USERNAME/fog-ai-anomaly-detection.git

# Aller dans le dossier
cd fog-ai-anomaly-detection

# Installer les dépendances
chmod +x setup.sh run.sh
./setup.sh

# Lancer le système
./run.sh
```

## 🔐 Authentification GitHub

Si GitHub demande une authentification:

### Option A: Token d'accès personnel (HTTPS)

1. Créer un token: https://github.com/settings/tokens
2. Sélectionner `repo` scope
3. Utiliser le token comme mot de passe

### Option B: SSH (recommandé)

```bash
# Générer une clé SSH (si pas déjà fait)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Ajouter à GitHub
cat ~/.ssh/id_ed25519.pub
# Copier et ajouter sur: https://github.com/settings/keys

# Utiliser SSH URL
git remote set-url origin git@github.com:USERNAME/fog-ai-anomaly-detection.git
```

## 📋 Vérification

```bash
# Voir les remotes
git remote -v

# Voir l'historique
git log --oneline

# Voir le statut
git status
```

## 🆘 Problèmes courants

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/USERNAME/fog-ai-anomaly-detection.git
```

### "Permission denied"
- Vérifiez que le dépôt existe sur GitHub
- Utilisez un token d'accès personnel
- Ou configurez SSH

### "Repository not found"
- Vérifiez l'URL du dépôt
- Assurez-vous que le dépôt existe sur GitHub

---

**Besoin d'aide?** Voir `GIT_SETUP.md` pour plus de détails.

