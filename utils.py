import pandas as pd
from datetime import datetime

EXCEL_PATH = "budget.xlsx"

def загрузить_данные():
    try:
        return pd.read_excel(EXCEL_PATH)
    except:
        return pd.DataFrame(columns=["Дата", "Тип", "Категория", "Подкатегория", "Сумма"])

def сохранить_запись(тип, категория, подкатегория, сумма, дата=None):
    df = загрузить_данные()
    запись = {
        "Дата": дата or datetime.today().strftime('%Y-%m-%d'),
        "Тип": тип,
        "Категория": категория,
        "Подкатегория": подкатегория,
        "Сумма": float(сумма)
    }
    df = pd.concat([df, pd.DataFrame([запись])], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)

def отфильтровать_по_датам(df, start, end):
    df["Дата"] = pd.to_datetime(df["Дата"])
    if start:
        df = df[df["Дата"] >= pd.to_datetime(start)]
    if end:
        df = df[df["Дата"] <= pd.to_datetime(end)]
    return df
