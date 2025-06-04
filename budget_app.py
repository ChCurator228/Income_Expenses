from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)
EXCEL_PATH = "budget.xlsx"

# Категории
категории_доход = {
    "Работа": ["Зарплата", "Фриланс", "Бонусы"],
    "Инвестиции": ["Дивиденды", "Проценты"],
    "Прочее": ["Подарки", "Возвраты"]
}

категории_расход = {
    "Еда": ["Продукты", "Кафе", "Фастфуд"],
    "Транспорт": ["Автобус", "Метро", "Такси"],
    "Коммунальные платежи": ["Интернет", "Электричество", "Вода"],
    "Развлечения": ["Кино", "Игры", "Подписки"]
}

# Загрузка и сохранение
def загрузить_данные():
    try:
        return pd.read_excel(EXCEL_PATH)
    except:
        return pd.DataFrame(columns=["Дата", "Тип", "Категория", "Подкатегория", "Сумма"])

def сохранить_запись(тип, категория, подкатегория, сумма):
    df = загрузить_данные()
    новая = {
        "Дата": datetime.today().strftime('%Y-%m-%d'),
        "Тип": тип,
        "Категория": категория,
        "Подкатегория": подкатегория,
        "Сумма": float(сумма)
    }
    df = pd.concat([df, pd.DataFrame([новая])], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)

# HTML
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Бюджет</title>
    <meta charset="utf-8">
</head>
<body style="font-family:sans-serif; max-width:800px; margin:auto;">
    <h2>💰 Учёт доходов и расходов</h2>

    <form method="post">
        <label>Тип:</label>
        <select name="тип" onchange="this.form.submit()">
            <option value="Доход" {% if тип == 'Доход' %}selected{% endif %}>Доход</option>
            <option value="Расход" {% if тип == 'Расход' %}selected{% endif %}>Расход</option>
        </select>

        <label>Категория:</label>
        <select name="категория" onchange="this.form.submit()">
            {% for cat in категории %}
                <option value="{{ cat }}" {% if cat == категория %}selected{% endif %}>{{ cat }}</option>
            {% endfor %}
        </select>

        <label>Подкатегория:</label>
        <select name="подкатегория">
            {% for sub in подкатегории %}
                <option value="{{ sub }}">{{ sub }}</option>
            {% endfor %}
        </select>

        <label>Сумма:</label>
        <input type="number" step="0.01" name="сумма" required>
        <button type="submit">Сохранить</button>
    </form>

    <hr>

    <h3>📅 Фильтр по дате</h3>
    <form method="get">
        <label>С:</label>
        <input type="date" name="start_date" value="{{ start_date }}">
        <label>По:</label>
        <input type="date" name="end_date" value="{{ end_date }}">
        <button type="submit">Показать</button>
    </form>

    <h4>📋 Записи за выбранный период:</h4>
    <table border="1" cellpadding="5">
        <tr><th>Дата</th><th>Тип</th><th>Категория</th><th>Подкатегория</th><th>Сумма</th></tr>
        {% for row in записи %}
        <tr>
            <td>{{ row['Дата'] }}</td>
            <td>{{ row['Тип'] }}</td>
            <td>{{ row['Категория'] }}</td>
            <td>{{ row['Подкатегория'] }}</td>
            <td>{{ row['Сумма'] }}</td>
        </tr>
        {% endfor %}
    </table>

    <p><strong>Итого:</strong> {{ итог }}</p>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def home():
    тип = request.form.get("тип", "Доход")
    категория = request.form.get("категория", list((категории_доход if тип == "Доход" else категории_расход).keys())[0])
    подкатегории = (категории_доход if тип == "Доход" else категории_расход).get(категория, [])

    # Добавление записи
    if request.method == "POST" and "сумма" in request.form:
        подкатегория = request.form.get("подкатегория")
        сумма = request.form.get("сумма")

        if сумма.strip() == "":
            return "Ошибка: вы не указали сумму!"

        try:
            сохранить_запись(тип, категория, подкатегория, сумма)
            return redirect(url_for("home"))
        except ValueError:
            return "Ошибка: неверный формат суммы."

    # Обработка фильтра
    df = загрузить_данные()
    df["Дата"] = pd.to_datetime(df["Дата"])
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    отфильтровано = df.copy()

    if start_date:
        отфильтровано = отфильтровано[отфильтровано["Дата"] >= pd.to_datetime(start_date)]
    if end_date:
        отфильтровано = отфильтровано[отфильтровано["Дата"] <= pd.to_datetime(end_date)]

    записи = отфильтровано.to_dict(orient="records")
    итог = отфильтровано["Сумма"].sum()

    return render_template_string(TEMPLATE,
        тип=тип,
        категория=категория,
        категории=(категории_доход if тип == "Доход" else категории_расход).keys(),
        подкатегории=подкатегории,
        записи=записи,
        итог=итог,
        start_date=start_date,
        end_date=end_date
    )

if __name__ == "__main__":
    app.run(debug=True)
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# Категории
категории_доход = {
    "Работа": ["Зарплата", "Фриланс", "Бонусы"],
    "Инвестиции": ["Дивиденды", "Проценты"],
    "Прочее": ["Подарки", "Возвраты"]
}
категории_расход = {
    "Еда": ["Продукты", "Кафе", "Фастфуд"],
    "Транспорт": ["Автобус", "Метро", "Такси"],
    "Коммунальные": ["Интернет", "Электричество", "Вода"],
    "Развлечения": ["Кино", "Игры", "Подписки"]
}

excel_path = "budget.xlsx"
try:
    df = pd.read_excel(excel_path)
except:
    df = pd.DataFrame(columns=["Дата", "Тип", "Категория", "Подкатегория", "Сумма"])
    df.to_excel(excel_path, index=False)

def сохранить_запись(тип, категория, подкатегория, сумма):
    global df
    запись = {
        "Дата": datetime.today().strftime('%Y-%m-%d'),
        "Тип": тип,
        "Категория": категория,
        "Подкатегория": подкатегория,
        "Сумма": float(сумма)
    }
    df = pd.concat([df, pd.DataFrame([запись])], ignore_index=True)
    df.to_excel(excel_path, index=False)

def построить_график():
    расходы = df[df["Тип"] == "Расход"]
    график = расходы.groupby("Категория")["Сумма"].sum()
    график.plot(kind="pie", autopct="%1.1f%%", figsize=(6, 6), title="Расходы по категориям")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

def отфильтровать_по_датам(start, end):
    try:
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        return df[(df["Дата"] >= start) & (df["Дата"] <= end)]
    except:
        messagebox.showerror("Ошибка", "Введите корректные даты!")
        return pd.DataFrame()

def экспортировать_csv(таблица_df):
    файл = filedialog.asksaveasfilename(defaultextension=".csv")
    if файл:
        таблица_df.to_csv(файл, index=False)
        messagebox.showinfo("Успешно", "Файл сохранён")

# GUI
root = tk.Tk()
root.title("Учёт бюджета")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

### Вкладка 1: Добавить запись
frame1 = ttk.Frame(notebook)
notebook.add(frame1, text="Добавить запись")

combo_тип = ttk.Combobox(frame1, values=["Доход", "Расход"])
combo_тип.grid(row=0, column=1, padx=5, pady=5)
combo_тип.current(0)

def обновить_категории(*_):
    тип = combo_тип.get()
    категории = категории_доход if тип == "Доход" else категории_расход
    combo_категория["values"] = list(категории.keys())
    combo_категория.current(0)
    обновить_подкатегории()

def обновить_подкатегории(*_):
    тип = combo_тип.get()
    категория = combo_категория.get()
    подкат = категории_доход if тип == "Доход" else категории_расход
    combo_подкатегория["values"] = подкат.get(категория, [])
    if подкат.get(категория):
        combo_подкатегория.current(0)

combo_тип.bind("<<ComboboxSelected>>", обновить_категории)

ttk.Label(frame1, text="Тип:").grid(row=0, column=0)
ttk.Label(frame1, text="Категория:").grid(row=1, column=0)
combo_категория = ttk.Combobox(frame1)
combo_категория.grid(row=1, column=1)
combo_категория.bind("<<ComboboxSelected>>", обновить_подкатегории)

ttk.Label(frame1, text="Подкатегория:").grid(row=2, column=0)
combo_подкатегория = ttk.Combobox(frame1)
combo_подкатегория.grid(row=2, column=1)

ttk.Label(frame1, text="Сумма:").grid(row=3, column=0)
entry_сумма = ttk.Entry(frame1)
entry_сумма.grid(row=3, column=1)

def сохранить():
    try:
        сохранить_запись(combo_тип.get(), combo_категория.get(), combo_подкатегория.get(), entry_сумма.get())
        messagebox.showinfo("Успешно", "Запись добавлена!")
        entry_сумма.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

ttk.Button(frame1, text="Сохранить", command=сохранить).grid(row=4, columnspan=2, pady=10)
обновить_категории()

### Вкладка 2: Таблица всех записей
frame2 = ttk.Frame(notebook)
notebook.add(frame2, text="Все записи")

tree = ttk.Treeview(frame2, columns=list(df.columns), show="headings")
for col in df.columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(fill="both", expand=True)

def обновить_таблицу():
    for i in tree.get_children():
        tree.delete(i)
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

обновить_таблицу()

### Вкладка 3: Фильтр и отчёт
frame3 = ttk.Frame(notebook)
notebook.add(frame3, text="Отчёт/Фильтр")

ttk.Label(frame3, text="С даты (гггг-мм-дд):").grid(row=0, column=0)
entry_start = ttk.Entry(frame3)
entry_start.grid(row=0, column=1)

ttk.Label(frame3, text="По дату:").grid(row=1, column=0)
entry_end = ttk.Entry(frame3)
entry_end.grid(row=1, column=1)

output = tk.Text(frame3, height=10, width=50)
output.grid(row=3, column=0, columnspan=2, pady=10)

def показать_отчёт():
    данные = отфильтровать_по_датам(entry_start.get(), entry_end.get())
    if not данные.empty:
        итог = данные.groupby("Тип")["Сумма"].sum()
        output.delete("1.0", tk.END)
        output.insert(tk.END, f"Доход: {итог.get('Доход', 0):.2f} ₽\n")
        output.insert(tk.END, f"Расход: {итог.get('Расход', 0):.2f} ₽\n")
    else:
        output.delete("1.0", tk.END)
        output.insert(tk.END, "Нет данных для отображения.")

ttk.Button(frame3, text="Показать отчёт", command=показать_отчёт).grid(row=2, column=0, pady=5)
ttk.Button(frame3, text="Экспорт CSV", command=lambda: экспортировать_csv(отфильтровать_по_датам(entry_start.get(), entry_end.get()))).grid(row=2, column=1, pady=5)

### Вкладка 4: График
frame4 = ttk.Frame(notebook)
notebook.add(frame4, text="График")

ttk.Button(frame4, text="Показать график расходов", command=построить_график).pack(pady=20)

root.mainloop()
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

категории_доход = {
    "Работа": ["Зарплата", "Фриланс", "Бонусы"],
    "Инвестиции": ["Дивиденды", "Проценты"],
    "Прочее": ["Подарки", "Возвраты"]
}

категории_расход = {
    "Еда": ["Продукты", "Кафе", "Фастфуд"],
    "Транспорт": ["Автобус", "Метро", "Такси"],
    "Коммунальные платежи": ["Интернет", "Электричество", "Вода"],
    "Развлечения": ["Кино", "Игры", "Подписки"]
}

excel_path = "budget.xlsx"

try:
    df = pd.read_excel(excel_path, sheet_name="Учёт")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Дата", "Тип", "Категория", "Подкатегория", "Сумма"])
    df.to_excel(excel_path, sheet_name="Учёт", index=False)


def добавить_запись(тип, категория, подкатегория, сумма, дата):
    global df
    if not сумма:
        raise ValueError("Поле 'Сумма' не может быть пустым")

    новая_запись = {
        "Дата": дата,
        "Тип": тип,
        "Категория": категория,
        "Подкатегория": подкатегория,
        "Сумма": float(сумма)
    }
    df = pd.concat([df, pd.DataFrame([новая_запись])], ignore_index=True)
    df.to_excel(excel_path, sheet_name="Учёт", index=False)


def построить_график():
    расходы = df[df["Тип"] == "Расход"]
    if расходы.empty:
        messagebox.showinfo("Нет данных", "Нет данных о расходах для построения графика.")
        return
    график = расходы.groupby("Категория")["Сумма"].sum()
    график.plot(kind="pie", autopct="%1.1f%%", figsize=(6, 6), title="Расходы по категориям")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()


def запустить_gui():
    def обновить_категории(event=None):
        тип = combo_тип.get()
        доступные = list(категории_доход.keys() if тип == "Доход" else категории_расход.keys())
        combo_категория["values"] = доступные
        combo_категория.current(0)
        обновить_подкатегории()

    def обновить_подкатегории(event=None):
        тип = combo_тип.get()
        категория = combo_категория.get()
        подкатегории = категории_доход.get(категория, []) if тип == "Доход" else категории_расход.get(категория, [])
        combo_подкатегория["values"] = подкатегории
        if подкатегории:
            combo_подкатегория.current(0)

    def сохранить():
        try:
            добавить_запись(
                combo_тип.get(),
                combo_категория.get(),
                combo_подкатегория.get(),
                entry_сумма.get(),
                entry_дата.get()
            )
            messagebox.showinfo("Успех", "Запись успешно добавлена!")
            entry_сумма.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    window = tk.Tk()
    window.title("Учёт доходов и расходов")
    window.geometry("350x260")
    window.resizable(False, False)

    ttk.Label(window, text="Тип:").grid(column=0, row=0, padx=5, pady=5, sticky="e")
    combo_тип = ttk.Combobox(window, values=["Доход", "Расход"], state="readonly")
    combo_тип.current(0)
    combo_тип.grid(column=1, row=0, padx=5, pady=5)
    combo_тип.bind("<<ComboboxSelected>>", обновить_категории)

    ttk.Label(window, text="Категория:").grid(column=0, row=1, padx=5, pady=5, sticky="e")
    combo_категория = ttk.Combobox(window, state="readonly")
    combo_категория.grid(column=1, row=1, padx=5, pady=5)
    combo_категория.bind("<<ComboboxSelected>>", обновить_подкатегории)

    ttk.Label(window, text="Подкатегория:").grid(column=0, row=2, padx=5, pady=5, sticky="e")
    combo_подкатегория = ttk.Combobox(window, state="readonly")
    combo_подкатегория.grid(column=1, row=2, padx=5, pady=5)

    ttk.Label(window, text="Сумма:").grid(column=0, row=3, padx=5, pady=5, sticky="e")
    entry_сумма = ttk.Entry(window)
    entry_сумма.grid(column=1, row=3, padx=5, pady=5)

    ttk.Label(window, text="Дата (ГГГГ-ММ-ДД):").grid(column=0, row=4, padx=5, pady=5, sticky="e")
    entry_дата = ttk.Entry(window)
    entry_дата.insert(0, datetime.today().strftime('%Y-%m-%d'))
    entry_дата.grid(column=1, row=4, padx=5, pady=5)

    btn_сохранить = ttk.Button(window, text="Сохранить", command=сохранить)
    btn_сохранить.grid(column=0, row=5, columnspan=2, pady=10)

    btn_график = ttk.Button(window, text="Показать график", command=построить_график)
    btn_график.grid(column=0, row=6, columnspan=2, pady=5)

    обновить_категории()
    window.mainloop()


if __name__ == "__main__":
    запустить_gui()
