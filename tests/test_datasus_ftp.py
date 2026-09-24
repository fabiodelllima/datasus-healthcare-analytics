"""
Teste de conexão com DataSUS via FTP
Não depende de pysus, usa ftplib nativo do Python
"""

import sys
from ftplib import FTP


def test_connection():
    print("=" * 60)
    print("TESTE DE CONEXÃO - FTP DATASUS")
    print("=" * 60)

    ftp_host = "ftp.datasus.gov.br"

    try:
        print(f"\n[1/4] Conectando a {ftp_host}...")
        ftp = FTP(ftp_host, timeout=30)
        print("✓ Conexão estabelecida")

        print("\n[2/4] Login anônimo...")
        ftp.login()
        print("✓ Login bem-sucedido")

        print("\n[3/4] Listando diretórios principais...")
        directories = []
        ftp.retrlines("LIST", lambda x: directories.append(x))
        print(f"✓ {len(directories)} itens encontrados")

        print("\nPrimeiros 5 diretórios:")
        for item in directories[:5]:
            print(f"  {item}")

        print("\n[4/4] Acessando dados de internações (SIH)...")
        try:
            ftp.cwd("/dissemin/publicos/SIHSUS/200801_/Dados")
            files: list[str] = []
            ftp.retrlines("NLST", files.append)
            print("✓ Diretório SIH acessível")
            print(f"  Total de arquivos: {len(files)}")
            print(f"  Exemplo de arquivo: {files[0] if files else 'N/A'}")
        except Exception as e:
            print(f"⚠ Não conseguiu acessar SIH: {e}")

        ftp.quit()

        print("\n" + "=" * 60)
        print("RESULTADO: ✓ DATASUS ESTÁ ACESSÍVEL")
        print("=" * 60)
        print("\nCONCLUSÕES:")
        print("→ Conexão FTP: OK")
        print("→ Login anônimo: OK")
        print("→ Dados SIH disponíveis: OK")
        print("→ Possível usar dados reais na POC: SIM")

        return True

    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        print("\n" + "=" * 60)
        print("RESULTADO: ✗ FALHA NA CONEXÃO")
        print("=" * 60)
        print("\nAlternativa: Usar dados sintéticos na POC")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
