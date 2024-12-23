# 🔐 CodeSigner

Un outil puissant et flexible pour signer et vérifier l'authenticité de votre code source. Protégez vos utilisateurs en leur permettant de vérifier l'intégrité de votre code.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Caractéristiques

- 🔑 Génération sécurisée de paires de clés RSA
- 📝 Signature de fichiers individuels ou de répertoires complets
- 🔍 Vérification facile de l'authenticité du code
- 🎯 Sélection des fichiers par extension
- 💾 Stockage des signatures dans un format JSON portable
- 🚀 Interface en ligne de commande simple et intuitive

## 📋 Prérequis

- Python 3.7 ou supérieur
- Package cryptography

## 🛠️ Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/ciscoderm/codesigner.git
cd codesigner
```

2. Installez les dépendances :
```bash
pip install cryptography
```

## 📖 Guide d'utilisation

### Génération des clés

Générez votre paire de clés RSA :
```bash
python codesigner.py generate-keys
```
Cela créera un dossier `keys` contenant :
- `private_key.pem` (🔒 gardez-la secrète !)
- `public_key.pem` (🌐 partagez-la avec vos utilisateurs)

### Signature de code

Signez tous les fichiers Python dans le répertoire courant :
```bash
python codesigner.py sign --extensions .py
```

Signez plusieurs types de fichiers dans un répertoire spécifique :
```bash
python codesigner.py sign --directory ./mon_projet --extensions .py .js .css
```

### Distribution de votre code

Pour permettre aux utilisateurs de vérifier votre code, fournissez :
1. 📦 Votre code source
2. 📄 Le fichier `signatures.json` généré
3. 🔑 Votre clé publique (`public_key.pem`)

### Vérification du code

Les utilisateurs peuvent vérifier l'authenticité du code avec :
```bash
python codesigner.py verify --public-key chemin/vers/public_key.pem
```

## 🎯 Exemples

### Exemple de projet Python

```bash
# Générer les clés
python codesigner.py generate-keys

# Signer tous les fichiers Python
python codesigner.py sign --extensions .py

# Vérifier les signatures
python codesigner.py verify --public-key ./keys/public_key.pem
```

La sortie ressemblera à :
```
src/main.py: ✓ Valide
tests/test_main.py: ✓ Valide
```

## 🔒 Sécurité

- Utilise RSA 2048 bits pour une sécurité optimale
- Implémente le padding PSS pour la signature
- Utilise SHA-256 pour le hachage des fichiers
- Stocke les clés privées de manière sécurisée

## ⚠️ Bonnes pratiques

1. Ne partagez JAMAIS votre clé privée
2. Conservez votre clé privée dans un endroit sûr
3. Signez à nouveau votre code après chaque modification
4. Distribuez votre clé publique via un canal sécurisé

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. 🍴 Forker le projet
2. 🔨 Créer une branche pour votre fonctionnalité
3. 📝 Commiter vos changements
4. 🚀 Pusher vers la branche
5. 🎉 Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📬 Contact

- Créé par [Votre Nom]
- Twitter: [@votre_twitter]
- GitHub: [@votre_github]

---

⭐️ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !
