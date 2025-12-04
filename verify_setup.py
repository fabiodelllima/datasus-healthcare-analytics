#!/usr/bin/env python3
"""
Script de verificação do ambiente
"""

import sys
import platform

def check_python_version():
    """Verifica versão Python"""
    version = sys.version_info
    print(f"[CHECK] Python {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor == 11:
        print("  [OK] Python 3.11 detectado")
        return True
    else:
        print("  [ERRO] Python 3.11 requerido")
        return False

def check_packages():
    """Verifica pacotes instalados"""
    required = {
        'pysus': '0.11.0',
        'pandas': '2.1.4',
        'numpy': '1.26.2',
        'matplotlib': '3.8.2',
        'seaborn': '0.13.0'
    }

    all_ok = True

    for package, expected_version in required.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"[CHECK] {package}: {version}")

            if version.startswith(expected_version.split('.')[0]):
                print("  [OK] Versão compatível")
            else:
                print(f"  [WARN] Esperado {expected_version}, encontrado {version}")

        except ImportError:
            print(f"[CHECK] {package}")
            print("  [ERRO] Não instalado")
            all_ok = False

    return all_ok

def check_directories():
    """Verifica estrutura de diretórios"""
    from pathlib import Path

    required_dirs = [
        'data/raw',
        'data/processed',
        'logs',
        'reports',
        'notebooks'
    ]

    all_ok = True

    for dir_path in required_dirs:
        path = Path(dir_path)
        print(f"[CHECK] Diretório: {dir_path}")

        if path.exists() and path.is_dir():
            print("  [OK] Existe")
        else:
            print("  [ERRO] Não encontrado")
            all_ok = False

    return all_ok

def check_internet():
    """Verifica conectividade com DataSUS"""
    import socket

    print("[CHECK] Conectividade DataSUS")

    try:
        socket.create_connection(("ftp.datasus.gov.br", 21), timeout=5)
        print("  [OK] FTP DataSUS acessível")
        return True
    except OSError:
        print("  [ERRO] Não foi possível conectar ao FTP DataSUS")
        return False

def main():
    """Executa todas as verificações"""
    print("="*60)
    print("VERIFICAÇÃO DO AMBIENTE - DataSUS Healthcare Analytics")
    print("="*60)
    print()

    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.machine()}")
    print()

    checks = {
        'Python Version': check_python_version(),
        'Packages': check_packages(),
        'Directories': check_directories(),
        'Internet': check_internet()
    }

    print()
    print("="*60)
    print("RESUMO")
    print("="*60)

    for check_name, result in checks.items():
        status = "[OK]" if result else "[FALHOU]"
        print(f"{status} {check_name}")

    print()

    if all(checks.values()):
        print("[SUCCESS] Ambiente configurado corretamente!")
        return 0
    else:
        print("[ERROR] Alguns checks falharam. Revise as mensagens acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
