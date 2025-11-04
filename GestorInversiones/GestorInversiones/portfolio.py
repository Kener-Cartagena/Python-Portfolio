import pandas as pd
from api_yfinance import get_current_price

def calculate_portfolio_metrics(operations):
    total_invested = 0.0
    total_value = 0.0
    net_profit = 0.0
    total_retirado = 0.0

    if not operations.empty:
        operations = operations.copy()
        operations['precio_actual'] = operations['ticker'].apply(get_current_price)

        # Solo usar operaciones tipo Compra
        compras = operations[operations['tipo'] == 'Compra'].copy()
        compras['valor_actual'] = compras['cantidad'] * compras['precio_actual']

        total_invested = (operations[operations['tipo'] == 'Compra']['cantidad'] * operations[operations['tipo'] == 'Compra']['precio']).sum() - \
                         (operations[operations['tipo'] == 'Venta']['cantidad'] * operations[operations['tipo'] == 'Venta']['precio']).sum()
        total_value = compras['valor_actual'].sum()
    

    # El saldo total real es el valor de tus acciones menos lo que retiraste
    total_balance = total_value
    total_invested = total_invested
    net_profit = total_balance - total_invested
    

    # Rendimiento
    profit_percentage = (net_profit / total_invested * 100) if total_invested > 0 else 0.0

    return {
        "total_balance": round(total_balance, 2),         # Valor actual del portafolio
        "total_invested": round(total_invested, 2),       # Lo que pagaste por tus compras
        "net_profit": round(net_profit, 2),               # Diferencia entre valor actual e inversión
        "profit_percentage": round(profit_percentage, 2)  # % de ganancia o pérdida
    }


def procesar_venta(operations_df, venta):
    ticker = venta["ticker"]
    cantidad_a_vender = venta["cantidad"]
    costo_total_vendido = venta["precio"]  # Aquí tú ingresarás cuánto pagaste por lo que estás vendiendo
    comision = venta["comision"]
    fecha = venta["fecha"]

    compras = operations_df[
        (operations_df["ticker"] == ticker) & 
        (operations_df["tipo"] == "Compra")
    ].copy()

    if compras.empty:
        raise ValueError(f"No tienes acciones de {ticker} para vender.")

    compras["fecha"] = pd.to_datetime(compras["fecha"])
    compras = compras.sort_values("fecha")

    total_disponible = compras["cantidad"].sum()
    if cantidad_a_vender > total_disponible:
        raise ValueError(f"No tienes suficientes acciones de {ticker} para vender ({cantidad_a_vender} > {total_disponible})")

    # ↓ Paso 1: Eliminar todas las compras del ticker
    operations_df = operations_df[~((operations_df["ticker"] == ticker) & (operations_df["tipo"] == "Compra"))]

    # ↓ Paso 2: Calcular cantidad restante
    cantidad_restante = total_disponible - cantidad_a_vender

    # ↓ Paso 3: Calcular nuevo precio total restante
    # Sumamos todos los precios pagados por compras originales
    total_pagado_anterior = (compras["precio"]).sum()
    costo_restante = total_pagado_anterior - costo_total_vendido

    if cantidad_restante > 0:
        nuevo_precio_unitario = costo_restante / cantidad_restante
        nuevo_precio = total_pagado_anterior - costo_total_vendido

        nueva_compra = {
            "fecha": fecha,
            "ticker": ticker,
            "cantidad": cantidad_restante,
            "precio": round(nuevo_precio, 2),
            "tipo": "Compra",
            "comision": 0.0  # Podrías ajustar esto si divides comisiones
        }

        operations_df = pd.concat([operations_df, pd.DataFrame([nueva_compra])], ignore_index=True)

    # ↓ Paso 4: Registrar la venta como operación
    nueva_venta = {
        "fecha": fecha,
        "ticker": ticker,
        "cantidad": cantidad_a_vender,
        "precio": venta["precio"],  # Aquí tú pondrás cuánto pagaste por esas acciones vendidas
        "tipo": "Venta",
        "comision": comision
    }

    operations_df = pd.concat([operations_df, pd.DataFrame([nueva_venta])], ignore_index=True)
    return operations_df.reset_index(drop=True)
