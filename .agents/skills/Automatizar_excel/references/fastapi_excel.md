# FastAPI + Excel como backend — Referencia

## API básica que sirve datos de un Excel

```python
# main.py
# Exponer datos de un archivo Excel como una API REST simple.
# Ejecutar con: uvicorn main:app --reload

from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# --- Configuración ---
RUTA_EXCEL = Path("data/input/productos.xlsx")
HOJA = "Inventario"


# --- Modelos Pydantic ---
class Producto(BaseModel):
    """Modelo de producto con validación automática de tipos."""
    codigo: str
    nombre: str
    precio: float
    stock: int
    categoria: str


# --- Estado global de la app (cache en memoria) ---
class EstadoApp:
    df: pd.DataFrame | None = None


estado = EstadoApp()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Cargar el Excel al iniciar la app y liberar recursos al cerrar.
    Esto evita leer el archivo en cada request (mucho más rápido).
    """
    print("🚀 Cargando datos desde Excel...")
    try:
        estado.df = pd.read_excel(RUTA_EXCEL, sheet_name=HOJA)
        print(f"✅ {len(estado.df)} productos cargados.")
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {RUTA_EXCEL}")
        estado.df = pd.DataFrame()

    yield  # La app corre aquí

    print("🛑 Cerrando app.")


app = FastAPI(
    title="API de Inventario",
    description="Consulta y actualiza inventario desde un archivo Excel.",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Endpoints ---

@app.get("/productos", response_model=list[Producto])
def listar_productos(
    categoria: Annotated[str | None, Query(description="Filtrar por categoría")] = None,
    stock_minimo: Annotated[int, Query(ge=0)] = 0,
) -> list[Producto]:
    """
    Retorna todos los productos, con filtros opcionales por categoría y stock mínimo.
    """
    if estado.df is None or estado.df.empty:
        raise HTTPException(status_code=503, detail="Datos no disponibles.")

    df = estado.df.copy()

    # Aplicar filtros solo si fueron proporcionados
    if categoria:
        df = df[df["categoria"].str.upper() == categoria.upper()]
    if stock_minimo > 0:
        df = df[df["stock"] >= stock_minimo]

    return df.to_dict(orient="records")


@app.get("/productos/{codigo}", response_model=Producto)
def obtener_producto(codigo: str) -> Producto:
    """Busca un producto específico por su código."""
    if estado.df is None or estado.df.empty:
        raise HTTPException(status_code=503, detail="Datos no disponibles.")

    resultado = estado.df[estado.df["codigo"] == codigo.upper()]

    if resultado.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Producto con código '{codigo}' no encontrado."
        )

    return resultado.iloc[0].to_dict()


@app.get("/resumen")
def resumen_inventario() -> dict:
    """Retorna métricas rápidas del inventario actual."""
    if estado.df is None or estado.df.empty:
        raise HTTPException(status_code=503, detail="Datos no disponibles.")

    return {
        "total_productos": len(estado.df),
        "valor_total_inventario": float((estado.df["precio"] * estado.df["stock"]).sum()),
        "productos_sin_stock": int((estado.df["stock"] == 0).sum()),
        "categorias": estado.df["categoria"].unique().tolist(),
    }


@app.post("/recargar")
def recargar_datos() -> dict:
    """Vuelve a leer el Excel sin reiniciar el servidor. Útil si el archivo cambió."""
    try:
        estado.df = pd.read_excel(RUTA_EXCEL, sheet_name=HOJA)
        return {"mensaje": f"✅ {len(estado.df)} registros recargados correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## requirements.txt mínimo para esta API

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
pandas==2.2.0
openpyxl==3.1.2
pydantic==2.7.0
```
