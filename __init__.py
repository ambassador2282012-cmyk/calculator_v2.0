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