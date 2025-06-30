# scripts/limpieza.py

import pandas as pd
import numpy as np

def cargar_csv(ruta):
    """Carga un archivo CSV y muestra su forma."""
    df = pd.read_csv(ruta)
    print(f"✅ Dataset cargado: {df.shape[0]:,} filas y {df.shape[1]} columnas.")
    return df

def revisar_nulos(df):
    """Devuelve el % de nulos por columna."""
    return df.isnull().mean().sort_values(ascending=False) * 100

def eliminar_duplicados(df):
    """Elimina duplicados y reporta cuántos había."""
    antes = df.shape[0]
    df = df.drop_duplicates()
    despues = df.shape[0]
    print(f"🧹 Duplicados eliminados: {antes - despues}")
    return df

def convertir_fechas(df, columnas):
    """Convierte una o varias columnas a datetime."""
    for col in columnas:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        print(f"📅 Convertida columna: {col}")
    return df

def imputar_nulos(df, estrategia='media'):
    """Imputa valores nulos en columnas numéricas."""
    for col in df.select_dtypes(include=np.number).columns:
        if df[col].isnull().any():
            if estrategia == 'media':
                valor = df[col].mean()
            elif estrategia == 'mediana':
                valor = df[col].median()
            elif estrategia == 'cero':
                valor = 0
            df[col] = df[col].fillna(valor)
            print(f"➕ Imputado {col} con {estrategia}")
    return df
