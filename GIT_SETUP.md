# Instructions pour pousser sur Git

Le dépôt Git local est déjà initialisé et le commit initial est fait.

## Option 1: GitHub (Recommandé)

### Étape 1: Créer un nouveau dépôt sur GitHub

1. Allez sur https://github.com/new
2. Nom du dépôt: `fog-ai-anomaly-detection` (ou autre nom)
3. **Ne cochez PAS** "Initialize with README" (le dépôt existe déjà)
4. Cliquez sur "Create repository"

### Étape 2: Connecter et pousser

```bash
cd fog-ai-anomaly-detection

# Ajouter le remote (remplacez USERNAME par votre nom d'utilisateur GitHub)
git remote add origin https://github.com/USERNAME/fog-ai-anomaly-detection.git

# Ou avec SSH (si vous avez configuré les clés SSH)
# git remote add origin git@github.com:USERNAME/fog-ai-anomaly-detection.git

# Pousser le code
git branch -M main
git push -u origin main
```

## Option 2: GitLab

### Étape 1: Créer un nouveau projet sur GitLab

1. Allez sur https://gitlab.com/projects/new
2. Créez un nouveau projet vide

### Étape 2: Connecter et pousser

```bash
cd fog-ai-anomaly-detection

# Ajouter le remote
git remote add origin https://gitlab.com/USERNAME/fog-ai-anomaly-detection.git

# Pousser le code
git branch -M main
git push -u origin main
```

## Option 3: Dépôt privé local (sans service cloud)

Si vous voulez juste transférer les fichiers manuellement:

```bash
# Créer une archive
cd ..
tar -czf fog-ai-anomaly-detection.tar.gz fog-ai-anomaly-detection/
# Ou sur Windows PowerShell:
Compress-Archive -Path fog-ai-anomaly-detection -DestinationPath fog-ai-anomaly-detection.zip
```

## Sur Kali Linux - Récupérer le projet

Une fois poussé sur GitHub/GitLab:

```bash
# Installer Git si nécessaire
sudo apt-get update
sudo apt-get install -y git

# Cloner le dépôt
git clone https://github.com/USERNAME/fog-ai-anomaly-detection.git
# Ou avec SSH:
# git clone git@github.com:USERNAME/fog-ai-anomaly-detection.git

# Aller dans le dossier
cd fog-ai-anomaly-detection

# Installer les dépendances
chmod +x setup.sh run.sh
./setup.sh

# Lancer le système
./run.sh
```

## Vérifier le statut Git

```bash
cd fog-ai-anomaly-detection
git status
git log --oneline
```

## Commandes Git utiles

```bash
# Voir les remotes configurés
git remote -v

# Changer l'URL du remote
git remote set-url origin NEW_URL

# Pousser les changements futurs
git add .
git commit -m "Description des changements"
git push
```

---

**Note**: Si vous utilisez HTTPS, GitHub vous demandera un token d'accès personnel au lieu d'un mot de passe.

Pour créer un token: https://github.com/settings/tokens

