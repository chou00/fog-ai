# Troubleshooting Guide

## 🔧 Problèmes Courants et Solutions

### 1. Erreur GPG sur Kali Linux

**Erreur:**
```
W: GPG error: http://kali.download/kali kali-rolling InRelease: 
The following signatures couldn't be verified because the public key is not available: 
NO_PUBKEY ED65462EC8D5E4C5
```

**Solution Rapide:**

```bash
# Option 1: Utiliser le script de correction
chmod +x fix_kali_gpg.sh
sudo ./fix_kali_gpg.sh

# Option 2: Correction manuelle
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5
sudo apt-get update

# Option 3: Installer le keyring Kali
sudo apt-get install -y kali-archive-keyring
sudo apt-get update
```

**Si les méthodes ci-dessus ne fonctionnent pas:**

```bash
# Télécharger et installer le keyring manuellement
wget -q -O - https://archive.kali.org/archive-key.asc | sudo apt-key add -
sudo apt-get update
```

---

### 2. Permission Denied pour Tshark

**Erreur:**
```
tshark: You don't have permission to capture on that device
```

**Solution:**

```bash
# Ajouter l'utilisateur au groupe wireshark
sudo usermod -a -G wireshark $USER

# Déconnexion/reconnexion nécessaire
# Ou utiliser newgrp
newgrp wireshark

# Vérifier
groups | grep wireshark
```

---

### 3. Mininet nécessite sudo

**Erreur:**
```
mininet.util.Error: Error creating network namespace
```

**Solution:**

```bash
# Toujours utiliser sudo avec Mininet
sudo python3 mininet/topology.py
```

---

### 4. Port déjà utilisé (Ryu Controller)

**Erreur:**
```
Address already in use: 6633
```

**Solution:**

```bash
# Trouver et tuer le processus
sudo lsof -i :6633
sudo kill -9 <PID>

# Ou tuer tous les processus Ryu
pkill -f ryu-manager
```

---

### 5. Module Python introuvable

**Erreur:**
```
ModuleNotFoundError: No module named 'ryu'
```

**Solution:**

```bash
# Réinstaller les dépendances
pip3 install -r requirements.txt --user

# Ou avec sudo si nécessaire
sudo pip3 install -r requirements.txt

# Vérifier l'installation
python3 -c "import ryu; print('OK')"
```

---

### 6. TensorFlow non disponible

**Erreur:**
```
ImportError: No module named 'tensorflow'
```

**Solution:**

```bash
# Option 1: Installer TensorFlow (optionnel)
pip3 install tensorflow --user

# Option 2: Utiliser Isolation Forest (pas besoin de TensorFlow)
python3 fog_agent.py --model isolation_forest
```

**Note:** Isolation Forest fonctionne sans TensorFlow et est recommandé pour la plupart des cas.

---

### 7. Erreur lors du clonage Git

**Erreur:**
```
fatal: unable to access 'https://github.com/...': SSL certificate problem
```

**Solution:**

```bash
# Désactiver temporairement la vérification SSL (non recommandé)
git config --global http.sslVerify false

# Ou mettre à jour les certificats
sudo apt-get update
sudo apt-get install -y ca-certificates
```

---

### 8. Scripts non exécutables

**Erreur:**
```
bash: ./setup.sh: Permission denied
```

**Solution:**

```bash
# Rendre les scripts exécutables
chmod +x setup.sh run.sh fix_kali_gpg.sh

# Vérifier
ls -l *.sh
```

---

### 9. Problème de réseau Mininet

**Erreur:**
```
Error creating network namespace
```

**Solution:**

```bash
# Nettoyer les namespaces existants
sudo mn -c

# Vérifier les permissions
sudo sysctl net.bridge.bridge-nf-call-iptables=0
```

---

### 10. Fog Agent ne détecte rien

**Problème:** Aucune anomalie détectée

**Solutions:**

```bash
# Vérifier que le trafic est généré
# Dans Mininet CLI:
h1 ping -c 10 10.0.0.2

# Vérifier les logs
tail -f logs/fog_fog1_detections.jsonl

# Générer du trafic anormal
h1 nmap -sS -p 1-1000 10.0.0.2

# Vérifier la queue de paquets
# Dans les logs, chercher "packet_queue_size"
```

---

## 🔍 Diagnostic

### Vérifier l'installation

```bash
# Vérifier Git
git --version

# Vérifier Python
python3 --version

# Vérifier Mininet
sudo mn --version

# Vérifier Ryu
ryu-manager --version

# Vérifier les dépendances Python
python3 -c "import numpy, sklearn, ryu; print('OK')"
```

### Vérifier les processus

```bash
# Voir tous les processus du projet
ps aux | grep -E "ryu|fog_agent|mininet"

# Tuer tous les processus
pkill -f ryu-manager
pkill -f fog_agent
sudo pkill -f mininet
```

### Vérifier les logs

```bash
# Lister tous les logs
ls -lh logs/

# Voir les dernières détections
tail -20 logs/fog_fog1_detections.jsonl

# Compter les anomalies
grep -c '"is_anomaly": true' logs/fog_fog1_detections.jsonl
```

---

## 📞 Obtenir de l'aide

1. Vérifier ce guide de dépannage
2. Consulter `README.md` pour la documentation complète
3. Vérifier les logs dans `logs/`
4. Vérifier que tous les prérequis sont installés

---

## 🛠️ Commandes de nettoyage

```bash
# Nettoyer complètement
sudo mn -c                    # Nettoyer Mininet
pkill -f ryu-manager          # Tuer Ryu
pkill -f fog_agent            # Tuer Fog agents
rm -rf logs/*.log logs/*.jsonl  # Nettoyer les logs
rm -rf models/*.pkl models/*.h5  # Nettoyer les modèles
```

---

**Dernière mise à jour:** Décembre 2024

