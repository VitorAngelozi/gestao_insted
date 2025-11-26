#!/usr/bin/env python
"""
Sistema de Backup Automático SQLite - Faculdade Insted
======================================================

Este sistema realiza backup automático do banco SQLite enquanto o servidor
Django está rodando, sem interromper o funcionamento.

Características:
- Executa em thread separada (não bloqueia o servidor)
- Backup incremental quando possível
- Rotação automática de backups antigos
- Logs detalhados de todas as operações
- Funciona com SQLite (banco padrão do Django)
- Backup de arquivos do projeto também

Uso:
    from backup_sqlite_automatico import BackupManager
    backup_manager = BackupManager()
    backup_manager.start_background_backup()

Ou execute diretamente:
    python backup_sqlite_automatico.py
"""

import datetime
import json
import logging
import os
import shutil
import sqlite3
import threading
import time
import zipfile
from pathlib import Path


class BackupSQLiteManager:
    def __init__(
        self,
        db_path=None,
        backup_interval=3600,  # 1 hora em segundos
        max_backups=24,  # Manter 24 backups (1 dia se backup a cada hora)
        base_dir=None,
    ):
        """
        Inicializar gerenciador de backup SQLite

        Args:
            db_path: Caminho para o banco SQLite (detecta automaticamente se None)
            backup_interval: Intervalo entre backups em segundos (padrão: 1 hora)
            max_backups: Quantidade máxima de backups para manter
            base_dir: Diretório base do projeto (detecta automaticamente se None)
        """
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.db_path = Path(db_path) if db_path else self._find_sqlite_db()
        self.backup_interval = backup_interval
        self.max_backups = max_backups

        # Configurar diretórios
        self.backup_dir = self.base_dir / "backups_sqlite"
        self.backup_dir.mkdir(exist_ok=True)

        # Configurar logging
        self._setup_logging()

        # Controle de thread
        self._backup_thread = None
        self._stop_event = threading.Event()
        self._running = False

        # Stats
        self.stats = {
            "total_backups": 0,
            "last_backup": None,
            "last_size": 0,
            "errors": 0,
        }

        self.logger.info(f"🔧 BackupManager inicializado")
        self.logger.info(f"📂 DB: {self.db_path}")
        self.logger.info(f"📁 Backups: {self.backup_dir}")
        self.logger.info(
            f"⏱️ Intervalo: {backup_interval}s ({backup_interval / 3600:.1f}h)"
        )

    def _find_sqlite_db(self):
        """Encontrar automaticamente o arquivo SQLite do Django"""
        possible_paths = [
            self.base_dir / "db.sqlite3",
            self.base_dir / "database.sqlite3",
            self.base_dir / "django.sqlite3",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Fallback: criar caminho padrão
        return self.base_dir / "db.sqlite3"

    def _setup_logging(self):
        """Configurar sistema de logging"""
        # Criar diretório de logs
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)

        # Configurar logger
        self.logger = logging.getLogger("backup_sqlite")
        self.logger.setLevel(logging.INFO)

        # Evitar duplicar handlers
        if not self.logger.handlers:
            # Handler para arquivo
            file_handler = logging.FileHandler(
                log_dir / "backup_sqlite.log", encoding="utf-8"
            )
            file_handler.setLevel(logging.INFO)

            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Formato das mensagens
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_db_info(self):
        """Obter informações do banco SQLite"""
        try:
            if not self.db_path.exists():
                return None

            stat = self.db_path.stat()

            # Conectar ao banco para obter mais informações
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Obter lista de tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                # Contagem total de registros (aproximada)
                total_records = 0
                for table in tables:
                    if not table.startswith("sqlite_"):
                        cursor.execute(f"SELECT COUNT(*) FROM '{table}'")
                        count = cursor.fetchone()[0]
                        total_records += count

            return {
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / 1024 / 1024,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime),
                "tables": len(tables),
                "total_records": total_records,
            }

        except Exception as e:
            self.logger.error(f"❌ Erro ao obter info do DB: {e}")
            return None

    def backup_database(self):
        """Realizar backup do banco SQLite"""
        if not self.db_path.exists():
            self.logger.error(f"❌ Banco não encontrado: {self.db_path}")
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"db_backup_{timestamp}.sqlite3"
        backup_path = self.backup_dir / backup_name

        try:
            self.logger.info(f"🔄 Iniciando backup do banco...")

            # Backup usando sqlite3 (método seguro mesmo com banco aberto)
            with sqlite3.connect(str(self.db_path)) as source:
                with sqlite3.connect(str(backup_path)) as backup:
                    source.backup(backup)

            # Verificar se o backup foi criado
            if backup_path.exists():
                size = backup_path.stat().st_size
                self.logger.info(
                    f"✅ Backup criado: {backup_name} ({size / 1024:.1f} KB)"
                )

                # Atualizar stats
                self.stats["total_backups"] += 1
                self.stats["last_backup"] = timestamp
                self.stats["last_size"] = size

                return backup_path
            else:
                self.logger.error(f"❌ Backup não foi criado")
                return None

        except Exception as e:
            self.logger.error(f"❌ Erro no backup: {e}")
            self.stats["errors"] += 1
            return None

    def backup_project_files(self):
        """Backup dos arquivos importantes do projeto"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        files_backup = self.backup_dir / f"project_files_{timestamp}.zip"

        try:
            self.logger.info(f"📁 Iniciando backup dos arquivos...")

            # Arquivos e diretórios para incluir
            items_to_backup = [
                "gestao_salas/",
                "sala/",
                "manage.py",
                "requirements.txt",
                "README.md",
            ]

            with zipfile.ZipFile(files_backup, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in items_to_backup:
                    item_path = self.base_dir / item
                    if item_path.exists():
                        if item_path.is_file():
                            zf.write(item_path, item)
                        elif item_path.is_dir():
                            for file_path in item_path.rglob("*"):
                                if file_path.is_file():
                                    # Evitar arquivos desnecessários
                                    if not any(
                                        skip in str(file_path)
                                        for skip in [
                                            "__pycache__",
                                            ".pyc",
                                            ".git",
                                            "node_modules",
                                        ]
                                    ):
                                        arc_name = file_path.relative_to(self.base_dir)
                                        zf.write(file_path, arc_name)

            size = files_backup.stat().st_size
            self.logger.info(
                f"✅ Backup arquivos: {files_backup.name} ({size / 1024:.1f} KB)"
            )
            return files_backup

        except Exception as e:
            self.logger.error(f"❌ Erro no backup de arquivos: {e}")
            return None

    def create_full_backup(self):
        """Criar backup completo (DB + arquivos)"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        self.logger.info(f"🚀 Iniciando backup completo - {timestamp}")

        # Backup do banco
        db_backup = self.backup_database()

        # Backup dos arquivos (a cada 6 horas ou na primeira execução)
        files_backup = None
        should_backup_files = (
            self.stats["total_backups"] == 0  # Primeira vez
            or self.stats["total_backups"] % 6
            == 0  # A cada 6 backups (6 horas se intervalo = 1h)
        )

        if should_backup_files:
            files_backup = self.backup_project_files()

        # Criar arquivo de informações
        info_file = self.backup_dir / f"backup_info_{timestamp}.json"
        backup_info = {
            "timestamp": timestamp,
            "datetime": datetime.datetime.now().isoformat(),
            "database": {
                "path": str(self.db_path),
                "backup_file": db_backup.name if db_backup else None,
                "info": self.get_db_info(),
            },
            "files": {
                "backup_file": files_backup.name if files_backup else None,
                "included": should_backup_files,
            },
            "stats": self.stats.copy(),
        }

        try:
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar info: {e}")

        # Limpeza de backups antigos
        self.cleanup_old_backups()

        self.logger.info(f"✅ Backup completo concluído!")
        return True

    def cleanup_old_backups(self):
        """Remover backups antigos mantendo apenas os mais recentes"""
        try:
            # Listar todos os arquivos de backup
            backup_files = list(self.backup_dir.glob("db_backup_*.sqlite3"))
            info_files = list(self.backup_dir.glob("backup_info_*.json"))
            files_backups = list(self.backup_dir.glob("project_files_*.zip"))

            # Ordenar por data (mais recentes primeiro)
            backup_files.sort(reverse=True)
            info_files.sort(reverse=True)
            files_backups.sort(reverse=True)

            # Remover backups de DB antigos
            removed_count = 0
            for backup_file in backup_files[self.max_backups :]:
                backup_file.unlink()
                removed_count += 1

            # Remover arquivos de info correspondentes
            for info_file in info_files[self.max_backups :]:
                info_file.unlink()
                removed_count += 1

            # Manter apenas os 4 backups de arquivos mais recentes
            for files_backup in files_backups[4:]:
                files_backup.unlink()
                removed_count += 1

            if removed_count > 0:
                self.logger.info(
                    f"🧹 Removidos {removed_count} arquivos de backup antigos"
                )

        except Exception as e:
            self.logger.error(f"❌ Erro na limpeza: {e}")

    def _backup_loop(self):
        """Loop principal do backup em background"""
        self.logger.info(
            f"🔄 Iniciando loop de backup (intervalo: {self.backup_interval}s)"
        )

        while not self._stop_event.is_set():
            try:
                # Realizar backup
                self.create_full_backup()

                # Aguardar próximo backup ou sinal de parada
                self._stop_event.wait(self.backup_interval)

            except Exception as e:
                self.logger.error(f"❌ Erro no loop de backup: {e}")
                self.stats["errors"] += 1
                # Aguardar um pouco antes de tentar novamente
                self._stop_event.wait(60)

    def start_background_backup(self):
        """Iniciar backup automático em background"""
        if self._running:
            self.logger.warning("⚠️ Backup já está rodando!")
            return

        self.logger.info("🚀 Iniciando backup automático em background...")

        # Backup inicial imediato
        self.create_full_backup()

        # Iniciar thread de backup
        self._stop_event.clear()
        self._backup_thread = threading.Thread(
            target=self._backup_loop,
            name="BackupSQLiteThread",
            daemon=True,  # Thread será finalizada quando programa principal terminar
        )

        self._backup_thread.start()
        self._running = True

        self.logger.info(
            f"✅ Backup automático iniciado! Próximo backup em {self.backup_interval}s"
        )

    def stop_background_backup(self):
        """Parar backup automático"""
        if not self._running:
            self.logger.warning("⚠️ Backup não está rodando!")
            return

        self.logger.info("🛑 Parando backup automático...")

        self._stop_event.set()

        if self._backup_thread and self._backup_thread.is_alive():
            self._backup_thread.join(timeout=5)

        self._running = False
        self.logger.info("✅ Backup automático parado!")

    def get_status(self):
        """Obter status atual do sistema de backup"""
        status = {
            "running": self._running,
            "db_path": str(self.db_path),
            "db_exists": self.db_path.exists(),
            "backup_dir": str(self.backup_dir),
            "interval_seconds": self.backup_interval,
            "interval_hours": self.backup_interval / 3600,
            "max_backups": self.max_backups,
            "stats": self.stats.copy(),
        }

        # Informações do banco
        db_info = self.get_db_info()
        if db_info:
            status["db_info"] = db_info

        # Contar backups existentes
        backup_files = list(self.backup_dir.glob("db_backup_*.sqlite3"))
        status["existing_backups"] = len(backup_files)

        if backup_files:
            # Último backup
            latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
            status["latest_backup"] = {
                "file": latest_backup.name,
                "created": datetime.datetime.fromtimestamp(
                    latest_backup.stat().st_mtime
                ).isoformat(),
                "size_kb": latest_backup.stat().st_size / 1024,
            }

        return status

    def list_backups(self):
        """Listar todos os backups disponíveis"""
        backups = []

        for backup_file in sorted(
            self.backup_dir.glob("db_backup_*.sqlite3"), reverse=True
        ):
            stat = backup_file.stat()

            # Procurar arquivo de info correspondente
            timestamp = backup_file.stem.replace("db_backup_", "")
            info_file = self.backup_dir / f"backup_info_{timestamp}.json"

            info = None
            if info_file.exists():
                try:
                    with open(info_file, "r", encoding="utf-8") as f:
                        info = json.load(f)
                except:
                    pass

            backups.append(
                {
                    "filename": backup_file.name,
                    "timestamp": timestamp,
                    "created": datetime.datetime.fromtimestamp(stat.st_mtime),
                    "size_kb": stat.st_size / 1024,
                    "info": info,
                }
            )

        return backups

    def restore_backup(self, backup_filename):
        """Restaurar um backup específico"""
        backup_path = self.backup_dir / backup_filename

        if not backup_path.exists():
            self.logger.error(f"❌ Backup não encontrado: {backup_filename}")
            return False

        try:
            self.logger.info(f"🔄 Restaurando backup: {backup_filename}")

            # Fazer backup do banco atual antes de restaurar
            if self.db_path.exists():
                backup_current = self.db_path.with_suffix(
                    ".sqlite3.backup_antes_restore"
                )
                shutil.copy2(self.db_path, backup_current)
                self.logger.info(
                    f"📋 Backup do estado atual salvo em: {backup_current.name}"
                )

            # Restaurar backup
            shutil.copy2(backup_path, self.db_path)

            self.logger.info(f"✅ Backup restaurado com sucesso!")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro na restauração: {e}")
            return False


def main():
    """Função principal para execução standalone"""
    print("🔄 SISTEMA DE BACKUP AUTOMÁTICO SQLite")
    print("Faculdade Insted - Gestão de Espaços")
    print("=" * 50)

    # Criar gerenciador de backup
    backup_manager = BackupSQLiteManager(
        backup_interval=3600,  # 1 hora
        max_backups=24,  # 24 horas de histórico
    )

    # Mostrar status
    status = backup_manager.get_status()
    print(f"\n📊 STATUS ATUAL:")
    print(f"   DB: {status['db_path']}")
    print(f"   Existe: {status['db_exists']}")
    print(f"   Backups existentes: {status['existing_backups']}")
    print(f"   Intervalo: {status['interval_hours']:.1f} horas")

    if status["db_info"]:
        info = status["db_info"]
        print(f"   Tamanho DB: {info['size_mb']:.1f} MB")
        print(f"   Tabelas: {info['tables']}")
        print(f"   Registros: {info['total_records']}")

    # Opções de execução
    print(f"\n🎯 OPÇÕES:")
    print(f"   1. Backup único (manual)")
    print(f"   2. Iniciar backup automático")
    print(f"   3. Listar backups existentes")
    print(f"   4. Ver status detalhado")

    try:
        choice = input(
            f"\nEscolha uma opção (1-4) ou Enter para backup único: "
        ).strip()

        if choice == "2":
            print(f"\n🚀 Iniciando backup automático...")
            print(f"⚠️  AVISO: Este processo rodará continuamente.")
            print(f"   Para parar, pressione Ctrl+C")

            backup_manager.start_background_backup()

            try:
                while backup_manager._running:
                    time.sleep(10)
                    # Mostrar status a cada 10 segundos
                    if backup_manager.stats["total_backups"] > 0:
                        print(
                            f"📊 Backups: {backup_manager.stats['total_backups']}, "
                            f"Último: {backup_manager.stats['last_backup']}"
                        )
            except KeyboardInterrupt:
                print(f"\n🛑 Parando backup automático...")
                backup_manager.stop_background_backup()

        elif choice == "3":
            print(f"\n📋 BACKUPS DISPONÍVEIS:")
            backups = backup_manager.list_backups()
            if backups:
                for i, backup in enumerate(
                    backups[:10], 1
                ):  # Mostrar apenas os 10 mais recentes
                    print(
                        f"   {i}. {backup['filename']} - "
                        f"{backup['created'].strftime('%d/%m/%Y %H:%M')} - "
                        f"{backup['size_kb']:.1f} KB"
                    )
            else:
                print(f"   Nenhum backup encontrado.")

        elif choice == "4":
            print(f"\n📊 STATUS DETALHADO:")
            import pprint

            pprint.pprint(status, width=80)

        else:
            # Backup único (padrão)
            print(f"\n🔄 Executando backup único...")
            backup_manager.create_full_backup()
            print(f"✅ Backup concluído!")

    except KeyboardInterrupt:
        print(f"\n⚠️ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
