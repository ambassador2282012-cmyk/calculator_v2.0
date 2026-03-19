import customtkinter as ctk
from tkinter import messagebox, filedialog
import re
import os
from pathlib import Path

ctk.set_appearance_mode("light")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class PriceCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("💰 Калькулятор цен с НДС 22%")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.nds_rate = 1.22
        self.price_file = "sample_price.txt"

        # 🔥 СПИСОК вместо словаря — все дубликаты!
        self.price_list = []  # [(имя, цена, номер_строки), ...]
        self.price_list = self.load_prices()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # 🎨 ГЛАВНАЯ ПАНЕЛЬ
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Toolbar
        self.main_frame.grid_rowconfigure(2, weight=1)  # Table
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Заголовок
        title = ctk.CTkLabel(self.main_frame, text="💎 Калькулятор цен + НДС 22%",
                             font=ctk.CTkFont(size=28, weight="bold"))
        title.grid(row=0, column=0, pady=(30, 20), sticky="ew")

        # 📊 ПАНЕЛЬ ИНСТРУМЕНТОВ (5 КНОПОК!)
        toolbar = ctk.CTkFrame(self.main_frame, height=60, corner_radius=10)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        toolbar.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)  # ✅ 5 колонок!

        # Кнопка 1: Загрузить
        self.load_btn = ctk.CTkButton(toolbar, text="📁 Загрузить",
                                      command=self.load_file, height=40)
        self.load_btn.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        # Кнопка 2: Сохранить
        self.save_btn = ctk.CTkButton(toolbar, text="💾 Сохранить",
                                      command=self.save_file, height=40)
        self.save_btn.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Кнопка 3: Добавить
        self.add_btn = ctk.CTkButton(toolbar, text="➕ Новый товар",
                                     command=self.add_item, height=40, fg_color="green")
        self.add_btn.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        # ПРОБЕЛ (пустая колонка)
        spacer = ctk.CTkFrame(toolbar, fg_color="transparent")
        spacer.grid(row=0, column=3, padx=5, pady=10, sticky="ew")

        # 🔍 ПОИСК (5-я колонка)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="🔍 Поиск товаров...",
                                         textvariable=self.search_var, height=40)
        self.search_entry.grid(row=0, column=4, padx=5, pady=10, sticky="ew")
        self.search_var.trace_add('write', self.on_search)  # ✅ Правильно!

        # 📋 ТАБЛИЦА (растягивается)
        self.table_frame = ctk.CTkScrollableFrame(self.main_frame,
                                                  label_text="📊 Прайс-лист")
        self.table_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))

        # Заголовки таблицы
        headers = ["№", "Наименование", "Цена", "Цена+НДС", "Действия"]
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=header,
                               font=ctk.CTkFont(size=13, weight="bold"),
                               width=140, anchor="center")
            lbl.grid(row=0, column=i, padx=2, pady=10, sticky="ew")

        # Статус бар
        self.status_var = ctk.StringVar(value=f"📈 Загружено: {len(self.price_list)} строк")
        status = ctk.CTkLabel(self.main_frame, textvariable=self.status_var,
                              font=ctk.CTkFont(size=12))
        status.grid(row=3, column=0, pady=10, sticky="ew")

    def load_prices(self):
        """🔥 СОХРАНЯЕМ ВСЕ ДУБЛИКАТЫ с номерами строк"""
        price_list = []

        try:
            if not os.path.exists(self.price_file):
                return price_list

            with open(self.price_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    original_line = line.strip()
                    if not original_line or original_line.startswith('#'):
                        continue

                    # Нормализуем
                    cleaned_line = re.sub(r'[\t\n\r]+', ' ', original_line)
                    cleaned_line = re.sub(r'\s+', ' ', cleaned_line)

                    # Находим последнее число
                    numbers = re.findall(r'(\d+[.,]?\d*)', cleaned_line)
                    if not numbers:
                        continue

                    price_str = numbers[-1].replace(',', '.')
                    try:
                        price = float(price_str)
                        name = cleaned_line[:cleaned_line.rfind(price_str)].strip()
                        if name:
                            # 🔥 СОХРАНЯЕМ: (имя, цена, номер_строки)
                            price_list.append((name, price, line_num))
                    except ValueError:
                        continue

            print(f"🎉 Загружено {len(price_list)} строк (все дубликаты!)")
            return price_list

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return price_list

    def save_file(self):
        """Сохранение"""
        try:
            with open(self.price_file, 'w', encoding='utf-8') as f:
                f.write("# Прайс-лист (Наименование Цена руб)\n\n")
                for name, price in sorted(self.prices.items()):
                    f.write(f"{name} {price:.2f} руб\n")
            messagebox.showinfo("✅ Сохранено", f"Файл: {self.price_file}\nТоваров: {len(self.prices)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{str(e)}")

    def load_file(self):
        """Загрузка файла"""
        filename = filedialog.askopenfilename(
            title="📂 Выберите прайс",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.price_file = filename
            self.prices = self.load_prices()
            self.refresh_table()

    def add_item(self):
        """Добавление товара"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("➕ Новый товар")
        dialog.geometry("450x300")
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text="📝 Наименование:",
                     font=ctk.CTkFont(size=14)).pack(pady=15)
        name_entry = ctk.CTkEntry(dialog, height=35, font=ctk.CTkFont(size=13))
        name_entry.pack(pady=5, padx=30, fill="x")

        ctk.CTkLabel(dialog, text="💰 Цена (руб):",
                     font=ctk.CTkFont(size=14)).pack(pady=15)
        price_entry = ctk.CTkEntry(dialog, height=35, font=ctk.CTkFont(size=13))
        price_entry.pack(pady=5, padx=30, fill="x")
        price_entry.focus()

        def save():
            name = name_entry.get().strip()
            try:
                price = float(price_entry.get().replace(',', '.'))
                if name and price >= 0:
                    self.prices[name] = price
                    self.refresh_table()
                    dialog.destroy()
                    messagebox.showinfo("✅ Добавлено", f"'{name}' - {price:.2f} руб")
                else:
                    messagebox.showerror("❌ Ошибка", "Заполните все поля!")
            except ValueError:
                messagebox.showerror("❌ Ошибка", "Цена должна быть числом!")

        ctk.CTkButton(dialog, text="💾 Сохранить", command=save,
                      height=40, fg_color="green").pack(pady=30)

    def refresh_table(self):
        """🔥 ВСЕ ДУБЛИКАТЫ + поиск — молниеносно!"""
        # Очистка
        for widget in self.table_frame.winfo_children()[1:]:
            widget.destroy()

        search_term = self.search_var.get().lower().strip()

        # 🔥 ФИЛЬТР: все строки где имя содержит поиск
        filtered_list = []
        for name, price, line_num in self.price_list:
            if not search_term or search_term in name.lower():
                filtered_list.append((name, price, line_num))

        # Макс 30 строк для скорости
        display_list = filtered_list[:30]

        for i, (name, price, line_num) in enumerate(display_list, 1):
            nds_price = price * self.nds_rate
            row = i + 1

            # № строки из файла
            ctk.CTkLabel(self.table_frame, text=f"{line_num}").grid(
                row=row, column=0, padx=5, pady=2, sticky="w")

            # Название (укорачиваем)
            short_name = name[:45] + "..." if len(name) > 45 else name
            ctk.CTkLabel(self.table_frame, text=short_name).grid(
                row=row, column=1, padx=5, pady=2, sticky="w")

            # Цена
            ctk.CTkLabel(self.table_frame, text=f"{price:.0f}₽").grid(
                row=row, column=2, padx=5, pady=2, sticky="e")

            # НДС
            ctk.CTkLabel(self.table_frame, text=f"{nds_price:.0f}₽",
                         text_color="green").grid(row=row, column=3, padx=5, pady=2, sticky="e")

            # Кнопки
            btn_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=4, padx=5, pady=2, sticky="ew")

            # Передаем номер строки для удаления
            ctk.CTkButton(btn_frame, text="✏️", width=25,
                          command=lambda ln=line_num: self.edit_by_line(ln)).pack(side="left", padx=1)
            ctk.CTkButton(btn_frame, text="🗑️", width=25, fg_color="#ef4444",
                          command=lambda ln=line_num: self.delete_by_line(ln)).pack(side="left", padx=1)

        # Точный статус
        self.status_var.set(f"📊 {len(display_list)} из {len(filtered_list)} строк")

    def edit_price(self, name):
        """Редактирование цены"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"✏️ Редактировать: {name}")
        dialog.geometry("400x220")

        ctk.CTkLabel(dialog, text=f"Текущая цена: {self.prices[name]:.2f} ₽",
                     font=ctk.CTkFont(size=14)).pack(pady=20)

        ctk.CTkLabel(dialog, text="Новая цена:",
                     font=ctk.CTkFont(size=14)).pack(pady=(10, 0))
        price_entry = ctk.CTkEntry(dialog, height=35)
        price_entry.insert(0, str(self.prices[name]))
        price_entry.pack(pady=10, padx=30, fill="x")
        price_entry.focus()

        def update():
            try:
                new_price = float(price_entry.get().replace(',', '.'))
                self.prices[name] = new_price
                self.refresh_table()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("❌ Ошибка", "Введите корректную цену!")

        ctk.CTkButton(dialog, text="✅ Обновить", command=update,
                      height=40, fg_color="#16a34a").pack(pady=25)

    def delete_item(self, name):
        """Удаление"""
        if messagebox.askyesno("🗑️ Удалить", f"Удалить товар '{name}'?"):
            del self.prices[name]
            self.refresh_table()

    def on_search(self, *args):
        """🔍 Поиск с задержкой 100мс"""
        self.after(100, self.refresh_table)

def debug_prices(self):
    """🔍 DEBUG: показывает весь прайс"""
    print("=== DEBUG ПРАЙС ===")
    print(f"Файл: {self.price_file}")
    print(f"Существует: {os.path.exists(self.price_file)}")
    print(f"Товаров загружено: {len(self.prices)}")
    for name, price in self.prices.items():
        print(f"  '{name}' → {price} руб")
    print("====================")


def main():
    app = PriceCalculator()
    app.mainloop()


if __name__ == "__main__":
    main()
