import pandas as pd
import os

OPERATIONS_CSV = "operations.csv"

def save_operation(operation):
    new_operation = pd.DataFrame([operation])
    if not os.path.exists(OPERATIONS_CSV):
        new_operation.to_csv(OPERATIONS_CSV, index=False)
    else:
        new_operation.to_csv(OPERATIONS_CSV, mode='a', header=False, index=False)

def load_operations():
    if os.path.exists(OPERATIONS_CSV):
        return pd.read_csv(OPERATIONS_CSV)
    return pd.DataFrame(columns=["fecha", "ticker", "cantidad", "precio", "tipo", "comision"])


'''def save_cash_transaction(transaction):
    new_transaction = pd.DataFrame([transaction])
    if not os.path.exists(CASH_CSV):
        new_transaction.to_csv(CASH_CSV, index=False)
    else:
        new_transaction.to_csv(CASH_CSV, mode='a', header=False, index=False)

def load_cash_transactions():
    if os.path.exists(CASH_CSV):
        return pd.read_csv(CASH_CSV)
    return pd.DataFrame(columns=["fecha", "tipo", "monto"])

def apply_inactivity_fee():
    operations = load_operations()
    cash_transactions = load_cash_transactions()
    if not operations.empty:
        last_operation_date = pd.to_datetime(operations['fecha']).max().date()  # Convertir Timestamp a date
        if (datetime.now().date() - last_operation_date).days >= 60:
            fee_transaction = {
                "fecha": datetime.now().date(),
                "tipo": "Retiro",
                "monto": 1.99
            }
            save_cash_transaction(fee_transaction)
            return True
    return False'''