# game_objects/weapon.py

# Добавим в класс Weapon метод для создания копии
class Weapon:
    def __init__(self, name, damage, accuracy, max_range, weight, ammo_capacity=30, initial_ammo=0):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.max_range = max_range # Максимальная дистанция (теперь не ограничивает выстрел)
        self.weight = weight
        self.ammo_capacity = ammo_capacity # Максимальное количество патронов
        self.max_ammo = ammo_capacity # Сохраняем максимальное значение
        # Если начальные патроны не заданы, используем 0 (или можно использовать max_ammo, если хочешь полные магазины по умолчанию)
        self.ammo = initial_ammo
        # --- НОВОЕ: Тип патронов ---
        self.ammo_type = self._get_ammo_type_by_name(name) # Определяем тип по имени оружия
        # --- КОНЕЦ НОВОГО ---

    def _get_ammo_type_by_name(self, name):
        """Simple mapping from weapon name to ammo type."""
        mapping = {
            "Пистолет": "9mm",
            "Автомат": "5.56mm",
            "Снайперская винтовка": "7.62mm",
            "Тяжелый пулемет": "7.62mm",
            "Дробовик": "12g"
        }
        return mapping.get(name, "unknown")

    # --- НОВАЯ ФУНКЦИЯ: Клонирование оружия ---
    def clone(self):
        """Create a copy of this weapon with the same properties but independent state."""
        # Создаём новый объект с теми же параметрами
        new_weapon = Weapon(
            name=self.name,
            damage=self.damage,
            accuracy=self.accuracy,
            max_range=self.max_range,
            weight=self.weight,
            ammo_capacity=self.ammo_capacity,
            initial_ammo=self.ammo # Копируем текущее количество патронов
        )
        return new_weapon
    # --- КОНЕЦ НОВОЙ ФУНКЦИИ ---

    def shoot(self):
        """Shoot and return damage if ammo available."""
        if self.ammo > 0:
            self.ammo -= 1
            return self.damage
        return 0 # Нет патронов, выстрел не удался

    def reload(self, ammo_item):
        """Reload weapon using ammo item. Returns ammo left in the item."""
        if ammo_item and ammo_item.ammo_type == self.ammo_type:
            # Сколько нужно до полного
            needed = self.ammo_capacity - self.ammo
            # Сколько можем взять из магазина
            taken = min(needed, ammo_item.ammo_count)
            # Добавляем к оружию
            self.ammo += taken
            # Убираем из магазина
            ammo_item.ammo_count -= taken
            # Возвращаем оставшееся количество в магазине
            return ammo_item.ammo_count
        return ammo_item.ammo_count if ammo_item else 0

    def get_info(self):
        """Get weapon info as dictionary."""
        return {
            'name': self.name,
            'damage': self.damage,
            'accuracy': self.accuracy,
            'max_range': self.max_range,
            'weight': self.weight,
            'ammo': self.ammo,
            'max_ammo': self.ammo_capacity,
            'ammo_type': self.ammo_type # --- НОВОЕ ---
        }
