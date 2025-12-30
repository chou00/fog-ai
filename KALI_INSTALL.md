# Installation sur Kali Linux

## 📥 Récupérer le projet depuis GitHub

### Si c'est la première fois (Cloner)

```bash
# Aller dans le répertoire souhaité (par exemple Desktop)
cd ~/Desktop

# Cloner le dépôt
git clone https://github.com/chou00/fog-ai.git

# Aller dans le dossier du projet
cd fog-ai
```

### Si le projet existe déjà (Mettre à jour)

```bash
# Aller dans le dossier du projet
cd ~/Desktop/fog-ai

# Récupérer les dernières modifications
git pull origin main
```

## 🔧 Installation complète

### Étape 1: Corriger le problème GPG (si nécessaire)

```bash
# Si vous avez une erreur GPG, exécutez d'abord:
chmod +x fix_kali_gpg.sh
sudo ./fix_kali_gpg.sh
```

### Étape 2: Installer les dépendances

```bash
# Rendre les scripts exécutables
chmod +x setup.sh run.sh fix_kali_gpg.sh

# Lancer l'installation
./setup.sh
```

### Étape 3: Lancer le système

```bash
# Lancer le système complet
./run.sh
```

## 🔄 Mettre à jour le projet

Pour récupérer les dernières modifications depuis GitHub:

```bash
# Dans le dossier du projet
cd ~/Desktop/fog-ai

# Récupérer les modifications
git pull origin main

# Si vous avez des modifications locales, utilisez:
git stash
git pull origin main
git stash pop
```

## 📋 Commandes Git utiles

```bash
# Voir l'état du dépôt
git status

# Voir les dernières modifications
git log --oneline -5

# Voir les différences
git diff

# Annuler des modifications locales
git checkout -- .

# Voir les branches distantes
git branch -r
```

## ⚠️ Résolution de conflits

Si vous avez des conflits lors du pull:

```bash
# Voir les fichiers en conflit
git status

# Résoudre manuellement les conflits dans les fichiers
# Puis:
git add .
git commit -m "Resolve conflicts"
```

## 🆘 Problèmes courants

### "Your branch is behind"
```bash
git pull origin main
```

### "Your branch has diverged"
```bash
git fetch origin
git reset --hard origin/main
```

### "Permission denied"
```bash
# Vérifier les permissions
ls -la

# Rendre exécutables
chmod +x *.sh
```

---

**Note:** Assurez-vous d'être dans le bon répertoire avant d'exécuter les commandes Git.

