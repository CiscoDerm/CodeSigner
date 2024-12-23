from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import base64
import json
import os
import argparse
from pathlib import Path
import sys

class CodeSigner:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.signatures_file = "signatures.json"

    def generate_keypair(self, save_path="./keys"):
        """Génère une nouvelle paire de clés RSA et les sauvegarde"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.private_key = private_key
        self.public_key = private_key.public_key()
        
        # Création du dossier keys s'il n'existe pas
        os.makedirs(save_path, exist_ok=True)
        
        # Sauvegarde des clés
        private_path = os.path.join(save_path, "private_key.pem")
        public_path = os.path.join(save_path, "public_key.pem")
        
        with open(private_path, 'wb') as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        with open(public_path, 'wb') as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        print(f"Clés générées et sauvegardées dans {save_path}")
        return private_path, public_path

    def sign_file(self, file_path: str) -> str:
        """Signe un fichier et enregistre la signature"""
        if not self.private_key:
            raise ValueError("Aucune clé privée n'a été chargée")
        
        # Lecture du contenu du fichier
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Calcul du hash SHA256 du contenu
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(content)
        file_hash = digest.finalize()
        
        # Signature du hash
        signature = self.private_key.sign(
            file_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Encodage de la signature en base64
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Sauvegarde de la signature dans le fichier JSON
        self.save_signature(file_path, signature_b64)
        
        return signature_b64

    def save_signature(self, file_path: str, signature: str):
        """Sauvegarde la signature dans un fichier JSON"""
        signatures = {}
        if os.path.exists(self.signatures_file):
            with open(self.signatures_file, 'r') as f:
                signatures = json.load(f)
        
        relative_path = os.path.relpath(file_path)
        signatures[relative_path] = signature
        
        with open(self.signatures_file, 'w') as f:
            json.dump(signatures, f, indent=4)

    def verify_file(self, file_path: str) -> bool:
        """Vérifie la signature d'un fichier"""
        if not self.public_key:
            raise ValueError("Aucune clé publique n'a été chargée")
        
        # Chargement des signatures
        if not os.path.exists(self.signatures_file):
            print(f"Fichier de signatures {self.signatures_file} non trouvé")
            return False
        
        with open(self.signatures_file, 'r') as f:
            signatures = json.load(f)
        
        relative_path = os.path.relpath(file_path)
        if relative_path not in signatures:
            print(f"Aucune signature trouvée pour {relative_path}")
            return False
        
        # Lecture du contenu du fichier
        with open(file_path, 'rb') as f:
            content = f.read()
        
        try:
            # Décodage de la signature
            signature = base64.b64decode(signatures[relative_path])
            
            # Calcul du hash du contenu
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(content)
            file_hash = digest.finalize()
            
            # Vérification de la signature
            self.public_key.verify(
                signature,
                file_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Erreur de vérification pour {relative_path}: {str(e)}")
            return False

    def load_private_key(self, key_path: str):
        """Charge une clé privée depuis un fichier"""
        with open(key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()

    def load_public_key(self, key_path: str):
        """Charge une clé publique depuis un fichier"""
        with open(key_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )

def sign_directory(directory: str, extensions: list = None):
    """Signe tous les fichiers d'un répertoire avec les extensions spécifiées"""
    signer = CodeSigner()
    
    # Chargement ou génération des clés
    if os.path.exists("keys/private_key.pem"):
        signer.load_private_key("keys/private_key.pem")
    else:
        signer.generate_keypair()
    
    # Parcours des fichiers
    for root, _, files in os.walk(directory):
        for file in files:
            if extensions is None or any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                print(f"Signature de {file_path}")
                signer.sign_file(file_path)

def verify_directory(directory: str, public_key_path: str):
    """Vérifie tous les fichiers signés d'un répertoire"""
    signer = CodeSigner()
    signer.load_public_key(public_key_path)
    
    if not os.path.exists(signer.signatures_file):
        print("Aucun fichier de signatures trouvé")
        return False
    
    # Chargement des signatures
    with open(signer.signatures_file, 'r') as f:
        signatures = json.load(f)
    
    all_valid = True
    for file_path in signatures.keys():
        if os.path.exists(file_path):
            is_valid = signer.verify_file(file_path)
            print(f"{file_path}: {'✓ Valide' if is_valid else '✗ Invalid'}")
            all_valid = all_valid and is_valid
        else:
            print(f"⚠️ Fichier manquant: {file_path}")
            all_valid = False
    
    return all_valid

def main():
    parser = argparse.ArgumentParser(description='Outil de signature de code')
    parser.add_argument('action', choices=['sign', 'verify', 'generate-keys'],
                       help='Action à effectuer')
    parser.add_argument('--directory', '-d', default='.',
                       help='Répertoire à traiter')
    parser.add_argument('--extensions', '-e', nargs='+',
                       help='Extensions de fichiers à signer (ex: .py .js)')
    parser.add_argument('--public-key', '-p',
                       help='Chemin vers la clé publique pour la vérification')
    
    args = parser.parse_args()
    
    if args.action == 'generate-keys':
        signer = CodeSigner()
        signer.generate_keypair()
    elif args.action == 'sign':
        sign_directory(args.directory, args.extensions)
    elif args.action == 'verify':
        if not args.public_key:
            print("Erreur: --public-key est requis pour la vérification")
            sys.exit(1)
        success = verify_directory(args.directory, args.public_key)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()