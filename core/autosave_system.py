# core/autosave_system.py
"""
Система автопсохранения игры
"""
import threading
import time
from datetime import datetime
from core.save_system import SaveSystem

class AutosaveSystem:
    def __init__(self, game_manager, interval=300):
        """
        Args:
            game_manager: Экземпляр GameManager
            interval: Интервал автопсохранения в секундах (по умолчанию 5 минут)
        """
        self.game_manager = game_manager
        self.interval = interval
        self.save_system = SaveSystem()
        self.running = False
        self.thread = None
        
    def start(self):
        """Запускает систему автопсохранения."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._autosave_loop, daemon=True)
        self.thread.start()
        print(f"Автопсохранение запущено (интервал: {self.interval} сек)")
    
    def stop(self):
        """Останавливает систему автопсохранения."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("Автопсохранение остановлено")
    
    def _autosave_loop(self):
        """Цикл автопсохранения."""
        while self.running:
            time.sleep(self.interval)
            
            # Проверяем, идет ли игра
            if (self.game_manager.current_map and 
                self.game_manager.game_state.state == 'game'):
                
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"autosave_{timestamp}.rsg"
                    self.save_system.save_game(self.game_manager, filename)
                    print(f"Автосохранение: {filename}")
                except Exception as e:
                    print(f"Ошибка автосохранения: {e}")
    
    def save_now(self):
        """Немедленное сохранение."""
        if self.game_manager.current_map and self.game_manager.game_state.state == 'game':
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"manual_autosave_{timestamp}.rsg"
                self.save_system.save_game(self.game_manager, filename)
                return filename
            except Exception as e:
                print(f"Ошибка немедленного сохранения: {e}")
        return None