import os
import sys
from pathlib import Path

from django.core.management.base import BaseCommand

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

try:
    from backup_sqlite_automatico import BackupSQLiteManager
except ImportError:
    BackupSQLiteManager = None


class Command(BaseCommand):
    help = "Backup automático SQLite - Faculdade Insted"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start",
            action="store_true",
            help="Iniciar backup automático",
        )
        parser.add_argument(
            "--stop", action="store_true", help="Parar backup automático"
        )
        parser.add_argument("--status", action="store_true", help="Mostrar status")
        parser.add_argument(
            "--backup-now", action="store_true", help="Fazer backup agora"
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=3600,
            help="Intervalo em segundos (padrão: 3600)",
        )

    def handle(self, *args, **options):
        if BackupSQLiteManager is None:
            self.stdout.write(self.style.ERROR("❌ Sistema de backup não disponível"))
            return

        backup_manager = BackupSQLiteManager(backup_interval=options["interval"])

        if options["start"]:
            self._start_backup(backup_manager)
        elif options["stop"]:
            self._stop_backup(backup_manager)
        elif options["status"]:
            self._show_status(backup_manager)
        elif options["backup_now"]:
            self._backup_now(backup_manager)
        else:
            self._show_help()

    def _start_backup(self, backup_manager):
        """Iniciar backup automático"""
        try:
            backup_manager.start_background_backup()
            self.stdout.write(self.style.SUCCESS("✅ Backup automático iniciado!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {e}"))

    def _stop_backup(self, backup_manager):
        """Parar backup"""
        try:
            backup_manager.stop_background_backup()
            self.stdout.write(self.style.SUCCESS("✅ Backup parado!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {e}"))

    def _show_status(self, backup_manager):
        """Mostrar status"""
        status = backup_manager.get_status()

        running = "🟢 RODANDO" if status["running"] else "🔴 PARADO"
        self.stdout.write(f"Status: {running}")

        if status.get("db_info"):
            info = status["db_info"]
            self.stdout.write(f"Banco: {info['size_mb']:.1f} MB")
            self.stdout.write(f"Tabelas: {info['tables']}")
            self.stdout.write(f"Registros: {info['total_records']}")

        stats = status["stats"]
        self.stdout.write(f"Total backups: {stats['total_backups']}")
        self.stdout.write(f"Último: {stats['last_backup'] or 'Nunca'}")

    def _backup_now(self, backup_manager):
        """Backup imediato"""
        try:
            backup_manager.create_full_backup()
            self.stdout.write(self.style.SUCCESS("✅ Backup concluído!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {e}"))

    def _show_help(self):
        """Mostrar ajuda"""
        self.stdout.write("🔄 BACKUP SQLITE - Comandos:")
        self.stdout.write("  --start      Iniciar backup automático")
        self.stdout.write("  --stop       Parar backup")
        self.stdout.write("  --status     Ver status")
        self.stdout.write("  --backup-now Backup imediato")
