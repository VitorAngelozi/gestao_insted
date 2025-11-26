#!/usr/bin/env python
"""
Servidor Django com Backup Automático - Faculdade Insted
========================================================

Servidor otimizado para rede local com backup automático SQLite.

Uso:
    python runserver_com_backup.py                    # Padrão: 0.0.0.0:8000
    python runserver_com_backup.py --port 8080        # Porta personalizada
    python runserver_com_backup.py --interval 1800    # Backup a cada 30min
    python runserver_com_backup.py --no-backup        # Sem backup

Servidor de Rede:
- Acessível por qualquer dispositivo na rede local
- Backup automático em background
- Logs detalhados
- Shutdown graceful com Ctrl+C
"""

import argparse
import atexit
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

# Adicionar diretório do projeto ao Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

try:
    from backup_sqlite_automatico import BackupSQLiteManager

    BACKUP_AVAILABLE = True
except ImportError:
    BACKUP_AVAILABLE = False
    print(
        "⚠️  Backup automático não disponível (backup_sqlite_automatico.py não encontrado)"
    )


class NetworkServerWithBackup:
    def __init__(
        self,
        host="0.0.0.0",
        port=8000,
        backup_interval=3600,
        max_backups=24,
        enable_backup=True,
    ):
        """
        Inicializar servidor de rede com backup automático

        Args:
            host: Host do servidor (0.0.0.0 para rede local)
            port: Porta do servidor
            backup_interval: Intervalo entre backups em segundos
            max_backups: Quantidade máxima de backups
            enable_backup: Se deve ativar backup automático
        """
        self.host = host
        self.port = port
        self.backup_interval = backup_interval
        self.max_backups = max_backups
        self.enable_backup = enable_backup and BACKUP_AVAILABLE

        # Controle de processos
        self.server_process = None
        self.backup_manager = None
        self.running = False
        self.start_time = time.time()

        # Configurar handlers para shutdown graceful
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self._cleanup)

        # Obter IP local para mostrar ao usuário
        self.local_ip = self._get_local_ip()

        print(f"🌐 SERVIDOR DE REDE - FACULDADE INSTED")
        print(f"{'=' * 50}")
        print(f"   Host: {host}:{port}")
        if self.local_ip and host == "0.0.0.0":
            print(f"   URL Local: http://localhost:{port}")
            print(f"   URL Rede: http://{self.local_ip}:{port}")
        print(f"   Backup: {'✅ Ativo' if self.enable_backup else '❌ Desabilitado'}")
        if self.enable_backup:
            print(f"   Intervalo: {backup_interval}s ({backup_interval / 3600:.1f}h)")
        print(f"{'=' * 50}")

    def _get_local_ip(self):
        """Obter IP local da máquina"""
        try:
            import socket

            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return None

    def _signal_handler(self, signum, frame):
        """Handler para sinais de término (Ctrl+C, etc.)"""
        print(f"\n🛑 Recebido sinal de parada...")
        self.stop()

    def _cleanup(self):
        """Limpeza no encerramento"""
        if self.running:
            self.stop()

    def start_backup_manager(self):
        """Iniciar gerenciador de backup"""
        if not self.enable_backup:
            return False

        try:
            print("🔄 Iniciando sistema de backup...")

            self.backup_manager = BackupSQLiteManager(
                backup_interval=self.backup_interval, max_backups=self.max_backups
            )

            # Backup inicial
            print("📦 Executando backup inicial...")
            self.backup_manager.create_full_backup()

            # Iniciar backup automático em background
            self.backup_manager.start_background_backup()

            print("✅ Backup automático iniciado!")
            return True

        except Exception as e:
            print(f"❌ Erro ao iniciar backup: {e}")
            print("⚠️  Continuando sem backup automático...")
            return False

    def start_django_server(self):
        """Iniciar servidor Django"""
        try:
            print(f"🚀 Iniciando servidor Django...")

            # Verificar se manage.py existe
            if not (project_dir / "manage.py").exists():
                print("❌ manage.py não encontrado!")
                return False

            # Comando para iniciar servidor
            cmd = [
                sys.executable,
                "manage.py",
                "runserver",
                f"{self.host}:{self.port}",
                "--noreload",  # Evita restart que interfere no backup
                "--nothreading",  # Melhor compatibilidade com backup SQLite
            ]

            # Configurar ambiente
            env = os.environ.copy()
            env["DJANGO_SETTINGS_MODULE"] = "gestao_salas.settings"

            # Iniciar processo do servidor
            self.server_process = subprocess.Popen(
                cmd,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env,
            )

            print(f"✅ Servidor iniciado (PID: {self.server_process.pid})")
            return True

        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            return False

    def show_access_info(self):
        """Mostrar informações de acesso"""
        print(f"\n📱 COMO ACESSAR:")
        print(f"   Local: http://localhost:{self.port}")
        if self.local_ip:
            print(f"   Rede: http://{self.local_ip}:{self.port}")
        print(f"\n📱 DISPOSITIVOS NA REDE PODEM ACESSAR:")
        if self.local_ip:
            print(f"   Celulares: http://{self.local_ip}:{self.port}")
            print(f"   Tablets: http://{self.local_ip}:{self.port}")
            print(f"   Outros PCs: http://{self.local_ip}:{self.port}")
        print(f"\n⚠️  Para parar o servidor: Ctrl+C")

    def monitor_server(self):
        """Monitorar servidor e mostrar logs importantes"""
        if not self.server_process:
            return

        print(f"📺 Monitorando servidor (mostrando apenas logs importantes)...")
        print(f"{'=' * 60}")

        try:
            for line in iter(self.server_process.stdout.readline, ""):
                if not self.running:
                    break

                line = line.strip()

                # Mostrar apenas logs importantes
                if any(
                    keyword in line.lower()
                    for keyword in [
                        "starting",
                        "quit",
                        "error",
                        "exception",
                        "traceback",
                        "warning",
                        "critical",
                        "watching",
                        "performing",
                    ]
                ):
                    print(f"[Django] {line}")

                # Verificar se servidor morreu
                if self.server_process.poll() is not None:
                    print("⚠️  Servidor Django finalizou!")
                    break

        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")

    def show_periodic_status(self):
        """Mostrar status periódico em thread separada"""
        while self.running:
            time.sleep(600)  # A cada 10 minutos
            if self.running:
                uptime = time.time() - self.start_time
                uptime_hours = uptime / 3600

                print(f"\n⏰ Status ({uptime_hours:.1f}h online):")
                print(f"   🌐 Servidor: http://{self.local_ip}:{self.port}")

                if self.backup_manager:
                    stats = self.backup_manager.stats
                    print(f"   📦 Backups: {stats['total_backups']}")
                    if stats.get("last_backup"):
                        print(f"   🕐 Último: {stats['last_backup']}")

    def start(self):
        """Iniciar todos os serviços"""
        if self.running:
            print("⚠️  Servidor já está rodando!")
            return False

        self.running = True

        # 1. Verificar banco SQLite
        db_path = project_dir / "db.sqlite3"
        if not db_path.exists():
            print("⚠️  Executando migrações iniciais...")
            try:
                subprocess.run(
                    [sys.executable, "manage.py", "migrate"],
                    cwd=project_dir,
                    check=True,
                    capture_output=True,
                )
                print("✅ Migrações concluídas!")
            except subprocess.CalledProcessError:
                print("❌ Erro nas migrações!")
                return False

        # 2. Iniciar backup automático
        backup_started = self.start_backup_manager()

        # 3. Iniciar servidor Django
        server_started = self.start_django_server()

        if not server_started:
            print("❌ Falha ao iniciar servidor!")
            self.stop()
            return False

        # 4. Aguardar servidor ficar pronto
        print("⏳ Aguardando servidor ficar disponível...")
        time.sleep(3)

        # 5. Mostrar informações de acesso
        self.show_access_info()

        # 6. Iniciar thread de status periódico
        status_thread = threading.Thread(target=self.show_periodic_status, daemon=True)
        status_thread.start()

        print(f"\n🎉 SERVIDOR DE REDE ATIVO!")
        print(f"{'=' * 60}")

        # 7. Monitorar servidor
        try:
            self.monitor_server()
        except KeyboardInterrupt:
            pass

        self.stop()
        return True

    def stop(self):
        """Parar todos os serviços"""
        if not self.running:
            return

        print(f"\n🛑 Parando servidor de rede...")
        self.running = False

        # Parar backup automático
        if self.backup_manager:
            try:
                print("📦 Parando backup automático...")
                self.backup_manager.stop_background_backup()
            except Exception as e:
                print(f"⚠️  Erro ao parar backup: {e}")

        # Parar servidor Django
        if self.server_process:
            try:
                print("🖥️  Parando servidor Django...")
                self.server_process.terminate()

                # Aguardar até 5 segundos
                try:
                    self.server_process.wait(timeout=5)
                    print("✅ Servidor parado gracefully")
                except subprocess.TimeoutExpired:
                    print("⚠️  Forçando parada...")
                    self.server_process.kill()
                    self.server_process.wait()

            except Exception as e:
                print(f"⚠️  Erro ao parar servidor: {e}")

        uptime = time.time() - self.start_time
        print(f"✅ Servidor finalizado (ficou online por {uptime / 3600:.1f}h)")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Servidor Django de Rede com Backup Automático SQLite"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para o servidor (padrão: 0.0.0.0 - rede local)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Porta para o servidor (padrão: 8000)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Intervalo entre backups em segundos (padrão: 3600 = 1 hora)",
    )
    parser.add_argument(
        "--max-backups",
        type=int,
        default=24,
        help="Quantidade máxima de backups (padrão: 24)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Iniciar servidor sem backup automático",
    )

    args = parser.parse_args()

    # Verificar diretório do projeto
    if not (project_dir / "manage.py").exists():
        print("❌ ERRO: Execute no diretório do projeto Django!")
        print(f"   Diretório atual: {project_dir}")
        sys.exit(1)

    try:
        # Criar servidor
        server = NetworkServerWithBackup(
            host=args.host,
            port=args.port,
            backup_interval=args.interval,
            max_backups=args.max_backups,
            enable_backup=not args.no_backup,
        )

        # Iniciar servidor
        success = server.start()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print(f"\n✅ Finalizado pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
