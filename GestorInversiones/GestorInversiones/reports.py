import pandas as pd
from api_yfinance import get_current_price

def generate_report(operations):
    report = operations.copy() if not operations.empty else pd.DataFrame(columns=["fecha", "ticker", "cantidad", "precio", "tipo", "comision"])
    
    # Inicializar totales
    total_invertido = 0
    dinero_neto = 0
    total_real = 0
    
    if not report.empty:
        # Asegurar tipos numéricos
        report['precio_compra'] = pd.to_numeric(report['precio'] * report['cantidad'], errors='coerce')
        report['cantidad'] = pd.to_numeric(report['cantidad'], errors='coerce')
        report['comision'] = pd.to_numeric(report['comision'], errors='coerce')

        report['precio_actual'] = report['ticker'].apply(get_current_price)
        report['valor_actual'] = report['cantidad'] * report['precio_actual']
        report['ganancia_perdida'] = report['valor_actual'] - report['precio_compra']

        # ↓↓↓ Filtrar solo compras activas para el resumen
        compras_activas = report[report['tipo'] == 'Compra']

        total_invertido = compras_activas['precio_compra'].sum()
        dinero_neto = compras_activas['valor_actual'].sum()
        total_real = dinero_neto - total_invertido

    # Define columns to exclude
    columns_to_exclude = ['comision', 'precio'] # Add any other columns you want to exclude here

    # Drop the excluded columns from the main report DataFrame
    # Use .reindex to handle cases where columns might not exist in an empty DataFrame
    report_columns_before_exclusion = report.columns.tolist()
    report = report.drop(columns=[col for col in columns_to_exclude if col in report.columns], errors='ignore')
    
    combined_df = pd.concat([report], ignore_index=True, sort=False)
    
    # Crear fila de resumen - SOLO con los totales en las columnas relevantes
    # Ensure summary_row also excludes the specified columns
    summary_data = {
        'fecha': ['TOTALES'],
        'ticker': [''],
        'cantidad': [''],
        'precio_compra': [total_invertido],  # Total invertido
        'tipo': [''],
        'precio_actual': [''],
        'valor_actual': [dinero_neto],  # Dinero neto
        'ganancia_perdida': [total_real],  # Total real
    }
    # Remove excluded columns from summary_data if they exist
    for col in columns_to_exclude:
        if col in summary_data:
            del summary_data[col]

    summary_row = pd.DataFrame(summary_data)
    
    # Asegurar que ambos DataFrames tengan las mismas columnas
    all_columns = list(set(combined_df.columns) | set(summary_row.columns))
    combined_df = combined_df.reindex(columns=all_columns, fill_value='')
    summary_row = summary_row.reindex(columns=all_columns, fill_value='')
    
    # Combinar todo
    final_report_df = pd.concat([combined_df, summary_row], ignore_index=True)
    
    # Definir el orden de columnas que quieres
    # The 'precio' column is already used to calculate 'precio_compra'
    # 'comision' is also explicitly excluded.
    desired_order = ['fecha', 'ticker', 'cantidad', 'tipo', 'precio_actual', 'precio_compra', 'valor_actual', 'ganancia_perdida']
    
    # Reordenar las columnas, manteniendo solo las que existen
    existing_columns = [col for col in desired_order if col in final_report_df.columns]
    remaining_columns = [col for col in final_report_df.columns if col not in desired_order and col not in columns_to_exclude] # Ensure these are also excluded
    
    # Orden final: primero las deseadas, luego las restantes (which should now be empty of excluded columns)
    final_column_order = existing_columns + remaining_columns
    final_report_df = final_report_df[final_column_order]
    
    # Guardar el reporte
    report_path = "reporte_inversiones.csv"
    final_report_df.to_csv(report_path, index=False)
    
    return report_path, final_report_df