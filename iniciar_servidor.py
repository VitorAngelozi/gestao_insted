#!/usr/bin/env python
"""
Iniciar Servidor - Faculdade Insted
===================================

Script simples para iniciar o servidor Django na rede local com backup automático.

Uso:
    python iniciar_servidor.py

O servidor ficará acessível em:
    - Local: http://localhost:8000
    - Rede: http://SEU_IP:8000
"""

import sys
from pathlib import Path

# Adicionar diretório do projeto
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def main():
    print("🌐 FACULDADE INSTED - SERVIDOR DE REDE")
    print("=" * 50)

    try:
        from runserver_com_backup import NetworkServerWithBackup

        # Criar servidor configurado para rede local
        server = NetworkServerWithBackup(
            host="0.0.0.0",  # Aceita conexões da rede
            port=8000,  # Porta padrão
            backup_interval=3600,  # Backup a cada 1 hora
            max_backups=24,  # Manter 24 backups (24h histórico)
            enable_backup=True,  # Backup automático ativo
        )

        # Iniciar servidor
        server.start()

    except ImportError:
        print("❌ Arquivos de backup não encontrados!")
        print("💡 Iniciando servidor simples sem backup...")

        import os
        import subprocess

        # Servidor Django básico
        os.chdir(project_dir)
        subprocess.run([sys.executable, "manage.py", "runserver", "0.0.0.0:8000"])

    except KeyboardInterrupt:
        print("\n✅ Servidor finalizado")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
