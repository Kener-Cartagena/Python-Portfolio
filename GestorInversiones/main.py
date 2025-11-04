import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from database import save_operation, load_operations
from reports import generate_report
from portfolio import calculate_portfolio_metrics, procesar_venta
from api_yfinance import get_current_price
import yfinance as yf
import requests
import os

# Configuración de la página
st.set_page_config(
    page_title="📈 Investment Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar clave de API de Alpha Vantage
ALPHA_VANTAGE_API_KEY = "4OIFQAGLLZYJ5P74"  # Obtéener clave en https://www.alphavantage.co/support/#api-key

# CSS personalizado para el dashboard
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 12px 24px;
        background-color: #f0f2f6;
        border-radius: 10px;
        color: #1f1f1f;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }

    .indicator-card {
        background: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem;
        text-align: center;
    }

    .indicator-value {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    .indicator-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sesión
if 'operations' not in st.session_state:
    st.session_state.operations = load_operations()

# Header principal
st.markdown("<h1 class='main-header'>📈 Investment Portfolio Tracker</h1>", unsafe_allow_html=True)

# Crear pestañas principales
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Operaciones", "💼 Portfolio", "📊 Dashboard", "📋 Reportes", "🔍 Análisis Fundamental"])

# ============================================
# TAB 1: OPERACIONES
# ============================================
with tab1:
    st.header("Registrar Operación (Compra/Venta)")
    
    with st.form(key="operation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            ticker = st.text_input("Ticker (ej. AAPL, MSFT)", max_chars=10).upper()
            quantity = st.number_input("Cantidad (puede ser fraccionada)", min_value=0.0, step=0.00001)
            price = st.number_input("Precio por acción ($)", min_value=0.0, step=0.01)
        
        with col2:
            operation_type = st.selectbox("Tipo de operación", ["Compra", "Venta"])
            commission = st.number_input("Comisión ($)", min_value=0.0, value=0.0, step=0.01)
            operation_date = st.date_input("Fecha", value=datetime.today())
        
        submit_button = st.form_submit_button("✅ Registrar Operación", use_container_width=True)

        if submit_button:
            if ticker and quantity > 0 and price > 0:
                operation = {
                    "fecha": operation_date,
                    "ticker": ticker,
                    "cantidad": quantity,
                    "precio": price,
                    "tipo": operation_type,
                    "comision": commission
                }

                try:
                    if operation_type == "Venta":
                        updated_ops = procesar_venta(st.session_state.operations.copy(), operation)
                        updated_ops.to_csv("operations.csv", index=False)
                        st.session_state.operations = updated_ops
                    else:
                        save_operation(operation)
                        st.session_state.operations = load_operations()

                    st.success("✅ Operación registrada con éxito.")
                    st.balloons()
                except ValueError as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("⚠️ Por favor, completa todos los campos correctamente.")
    
    st.markdown("---")
    
    # Gestionar operaciones existentes
    st.subheader("🗂 Gestionar Operaciones")
    operations = load_operations()

    if operations.empty:
        st.info("No hay operaciones registradas.")
    else:
        st.dataframe(operations.reset_index(drop=True), use_container_width=True)

        # Eliminar operaciones
        with st.expander("❌ Eliminar Operación"):
            index_to_delete = st.number_input(
                "Selecciona el número de la operación que deseas eliminar:",
                min_value=0,
                max_value=len(operations) - 1,
                step=1
            )

            if st.button("🗑️ Eliminar operación seleccionada"):
                operations = operations.drop(index_to_delete).reset_index(drop=True)
                operations.to_csv("operations.csv", index=False)
                st.success(f"✅ Operación #{index_to_delete} eliminada correctamente.")
                st.rerun()

# ============================================
# TAB 2: PORTFOLIO
# ============================================
with tab2:
    st.header("💼 Portfolio Actual")
    
    # Métricas principales
    metrics = calculate_portfolio_metrics(st.session_state.operations)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Saldo Total", f"${metrics['total_balance']:.2f}")
    with col2:
        st.metric("📊 Capital Invertido", f"${metrics['total_invested']:.2f}")
    with col3:
        delta_color = "normal" if metrics['net_profit'] >= 0 else "inverse"
        st.metric("💸 Ganancia Neta", f"${metrics['net_profit']:.2f}")
    with col4:
        st.metric("📈 Rendimiento", f"{metrics['profit_percentage']:.2f}%")
    
    st.markdown("---")
    
    # Tabla del portfolio
    if not st.session_state.operations.empty:
        with st.spinner("Actualizando precios..."):
            portfolio = st.session_state.operations.copy()
            portfolio['precio_actual'] = portfolio['ticker'].apply(get_current_price)
            portfolio['valor_actual'] = portfolio['cantidad'] * portfolio['precio_actual']
            portfolio['ganancia_perdida'] = portfolio['valor_actual'] - (portfolio['precio'] * portfolio['cantidad']) - portfolio['comision']
            portfolio['roi_%'] = ((portfolio['ganancia_perdida'] / (portfolio['precio'] * portfolio['cantidad'])) * 100).round(2)
        
        # Formatear para mostrar
        display_portfolio = portfolio.copy()
        display_portfolio['fecha'] = pd.to_datetime(display_portfolio['fecha']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_portfolio[['fecha', 'ticker', 'cantidad', 'precio', 'tipo', 'comision', 
                             'precio_actual', 'valor_actual', 'ganancia_perdida', 'roi_%']],
            use_container_width=True
        )
    else:
        st.info("📋 No hay operaciones registradas")

# ============================================
# TAB 3: DASHBOARD
# ============================================
with tab3:
    st.header("📊 Dashboard de Análisis")
    
    # Verificar si hay datos
    if st.session_state.operations.empty:
        st.warning("⚠️ No hay datos para mostrar. Registra algunas operaciones primero.")
    else:
        # Preparar datos para el dashboard
        df_operations = st.session_state.operations.copy()
        
        # Obtener precios actuales (con cache para optimizar)
        @st.cache_data(ttl=300)  # Cache por 5 minutos
        def get_dashboard_data(operations_data):
            df = operations_data.copy()
            df['precio_actual'] = df['ticker'].apply(get_current_price)
            df['valor_actual'] = df['cantidad'] * df['precio_actual']
            df['ganancia_perdida'] = df['valor_actual'] - (df['precio'] * df['cantidad']) - df['comision']
            df['fecha'] = pd.to_datetime(df['fecha'])
            return df
        
        with st.spinner("📊 Cargando dashboard..."):
            dashboard_df = get_dashboard_data(df_operations)
        
        # Métricas de resumen
        col1, col2, col3 = st.columns(3)
        
        total_invertido = (dashboard_df['precio'] * dashboard_df['cantidad']).sum()
        valor_actual = dashboard_df['valor_actual'].sum()
        ganancia_total = dashboard_df['ganancia_perdida'].sum()
        roi_total = (ganancia_total / total_invertido * 100) if total_invertido > 0 else 0
        
        with col1:
            st.metric("💰 Total Invertido", f"${total_invertido:,.2f}")
        with col2:
            st.metric("📈 Valor Actual", f"${valor_actual:,.2f}", 
                     delta=f"{((valor_actual/total_invertido-1)*100):+.2f}%" if total_invertido > 0 else "0%")
        with col3:
            st.metric("💸 Ganancia Total", f"${ganancia_total:,.2f}", 
                     delta=f"{roi_total:+.2f}%")
        
        st.markdown("---")
        
        # Crear dos columnas para gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de distribución por ticker
            st.subheader("🥧 Distribución del Portfolio")
            
            allocation = dashboard_df.groupby('ticker').agg({
                'valor_actual': 'sum'
            }).reset_index()
            
            fig_pie = px.pie(
                allocation,
                values='valor_actual',
                names='ticker',
                title="Valor por Ticker",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Gráfico de rendimiento por ticker
            st.subheader("📊 Rendimiento por Ticker")
            
            performance = dashboard_df.groupby('ticker').agg({
                'ganancia_perdida': 'sum',
                'precio': lambda x: (x * dashboard_df.loc[x.index, 'cantidad']).sum()  # Total invertido por ticker
            }).reset_index()
            
            performance['roi_%'] = (performance['ganancia_perdida'] / performance['precio'] * 100).round(2)
            
            fig_bar = px.bar(
                performance.sort_values('roi_%', ascending=True),
                x='roi_%',
                y='ticker',
                title="ROI por Ticker (%)",
                color='roi_%',
                color_continuous_scale='RdYlGn',
                orientation='h'
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Evolución temporal
        st.subheader("📈 Evolución Temporal del Portfolio")
        
        # Crear datos para evolución temporal
        dashboard_df_sorted = dashboard_df.sort_values('fecha').copy()
        dashboard_df_sorted['valor_acumulado'] = dashboard_df_sorted['valor_actual'].cumsum()
        dashboard_df_sorted['inversion_acumulada'] = (dashboard_df_sorted['precio'] * dashboard_df_sorted['cantidad']).cumsum()
        
        fig_evolution = go.Figure()
        
        fig_evolution.add_trace(go.Scatter(
            x=dashboard_df_sorted['fecha'],
            y=dashboard_df_sorted['inversion_acumulada'],
            mode='lines+markers',
            name='Inversión Acumulada',
            line=dict(color='#ff7f0e', width=3),
            fill='tonexty'
        ))
        
        fig_evolution.add_trace(go.Scatter(
            x=dashboard_df_sorted['fecha'],
            y=dashboard_df_sorted['valor_acumulado'],
            mode='lines+markers',
            name='Valor Actual',
            line=dict(color='#1f77b4', width=3),
            fill='tonexty'
        ))
        
        fig_evolution.update_layout(
            title="Evolución del Portfolio",
            xaxis_title="Fecha",
            yaxis_title="Valor ($)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_evolution, use_container_width=True)
        
        # Insights automáticos
        st.subheader("🔍 Insights Automáticos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Mejores Performers:**")
            top_performers = dashboard_df.nlargest(3, 'ganancia_perdida')[['ticker', 'ganancia_perdida']]
            for _, row in top_performers.iterrows():
                st.success(f"**{row['ticker']}**: ${row['ganancia_perdida']:,.2f}")
        
        with col2:
            st.markdown("**📉 Peores Performers:**")
            worst_performers = dashboard_df.nsmallest(3, 'ganancia_perdida')[['ticker', 'ganancia_perdida']]
            for _, row in worst_performers.iterrows():
                st.error(f"**{row['ticker']}**: ${row['ganancia_perdida']:,.2f}")

# ============================================
# TAB 4: REPORTES
# ============================================
with tab4:
    st.header("📋 Generar Reportes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📊 ¿Qué incluye el reporte?
        - 💰 Todas las operaciones con precios actualizados
        - 📈 Cálculo automático de ganancias/pérdidas
        - 📊 Resumen de totales y métricas principales
        - 💾 Archivo CSV listo para Excel
        """)
    
    with col2:
        if st.button("🔄 Generar Reporte Completo", type="primary", use_container_width=True):
            with st.spinner("Generando reporte..."):
                report_path, report_df = generate_report(st.session_state.operations)
            
            st.success("✅ Reporte generado exitosamente!")
            
            # Mostrar métricas del reporte generado
            if os.path.exists(report_path):
                with open(report_path, "rb") as file:
                    file_data = file.read()
                    
                st.download_button(
                    label="⬇️ Descargar Reporte CSV",
                    data=file_data,
                    file_name="reporte_inversiones.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Mostrar vista previa del reporte
                st.markdown("### 👀 Vista Previa del Reporte")
                try:
                    preview_df = pd.read_csv(report_path)
                    st.dataframe(preview_df, use_container_width=True)
                except Exception as e:
                    st.error(f"Error al mostrar vista previa: {str(e)}")

# ============================================
# TAB 5: ANÁLISIS FUNDAMENTAL
# ============================================
with tab5:
    st.header("🔍 Análisis Fundamental")
    
    # Sub-tabs para los dos modos
    mode_tab1, mode_tab2 = st.tabs(["📦 Mi Portafolio", "🔎 Explorar Empresa"])
    
    # Configuración de APIs adicionales 
FMP_API_KEY = "6GQvreiwEBQnbgDpl5RSpc4Ic1BqqIif"  
POLYGON_API_KEY = "yNQyvHiykwO8XUufJiPJwzGjhRJn3sr4"  

# Reemplaza la función get_fundamental_data y la sección de "Explorar Empresa"

@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_fundamental_data(ticker):
    """Obtener datos fundamentales de una empresa usando múltiples fuentes"""
    try:
        # Intentar con yfinance primero
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Calcular ROIC manualmente si es posible
        roic = None
        try:
            # ROIC = (Net Income) / (Total Capital)
            # O aproximado: ROE * (1 - Debt/Total Capital)
            roe = info.get('returnOnEquity')
            debt_to_equity = info.get('debtToEquity')
            if roe and debt_to_equity:
                # Aproximación simple de ROIC
                total_capital_ratio = 1 / (1 + (debt_to_equity / 100))
                roic = roe * total_capital_ratio * 100
        except:
            pass
        
        # Intentar obtener crecimiento de earnings de diferentes fuentes
        earnings_growth_lt = None
        try:
            # Usar earningsQuarterlyGrowth como proxy si está disponible
            quarterly_growth = info.get('earningsQuarterlyGrowth')
            if quarterly_growth:
                earnings_growth_lt = quarterly_growth * 100
        except:
            pass
        
        fundamentals = {
            'Ticker': ticker,
            'Name': info.get('longName', info.get('shortName', ticker)),
            'Margen Neto (%)': info.get('profitMargins', None) * 100 if info.get('profitMargins') else None,
            'ROIC (%)': roic,
            'Crecimiento EPS 5Y (%)': info.get('earningsGrowth', None) * 100 if info.get('earningsGrowth') else None,
            'Crecimiento Ganancias LT (%)': earnings_growth_lt,
            'P/E Ratio': info.get('trailingPE', None),
            'P/B Ratio': info.get('priceToBook', None),
            'Ratio Liquidez Inmediata': info.get('quickRatio', None),
            'Ratio Deuda/Patrimonio': info.get('debtToEquity', None) / 100 if info.get('debtToEquity') else None,
            'Rentabilidad Dividendo (%)': info.get('dividendYield', None) if info.get('dividendYield') else None,
            'Ratio Reparto Dividendos (%)': info.get('payoutRatio', None) * 100 if info.get('payoutRatio') else None
        }
        
        # Si faltan datos críticos, intentar con múltiples APIs
        missing_data = [k for k, v in fundamentals.items() if v is None and k not in ['Name', 'Ticker']]
        
        if len(missing_data) > 2:  # Si faltan más de 2 indicadores
            # 1. Intentar con Financial Modeling Prep (FMP)
            if FMP_API_KEY != "demo":
                try:
                    fmp_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={FMP_API_KEY}"
                    fmp_response = requests.get(fmp_url, timeout=10).json()
                    
                    if fmp_response and len(fmp_response) > 0:
                        fmp_data = fmp_response[0]  # Datos más recientes
                        
                        if fundamentals['ROIC (%)'] is None:
                            roic_fmp = fmp_data.get('returnOnCapitalEmployed')
                            if roic_fmp:
                                fundamentals['ROIC (%)'] = roic_fmp * 100
                        
                        if fundamentals['Margen Neto (%)'] is None:
                            net_profit_margin = fmp_data.get('netProfitMargin')
                            if net_profit_margin:
                                fundamentals['Margen Neto (%)'] = net_profit_margin * 100
                        
                        if fundamentals['P/E Ratio'] is None:
                            pe_ratio = fmp_data.get('priceEarningsRatio')
                            if pe_ratio:
                                fundamentals['P/E Ratio'] = pe_ratio
                        
                        if fundamentals['P/B Ratio'] is None:
                            pb_ratio = fmp_data.get('priceToBookRatio')
                            if pb_ratio:
                                fundamentals['P/B Ratio'] = pb_ratio
                        
                        if fundamentals['Ratio Liquidez Inmediata'] is None:
                            quick_ratio = fmp_data.get('quickRatio')
                            if quick_ratio:
                                fundamentals['Ratio Liquidez Inmediata'] = quick_ratio
                        
                        if fundamentals['Ratio Deuda/Patrimonio'] is None:
                            debt_equity = fmp_data.get('debtEquityRatio')
                            if debt_equity:
                                fundamentals['Ratio Deuda/Patrimonio'] = debt_equity
                    
                    # Intentar obtener datos de crecimiento de FMP
                    growth_url = f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?apikey={FMP_API_KEY}"
                    growth_response = requests.get(growth_url, timeout=10).json()
                    
                    if growth_response and len(growth_response) > 0:
                        growth_data = growth_response[0]
                        if fundamentals['Crecimiento EPS 5Y (%)'] is None:
                            eps_growth = growth_data.get('fiveYEarRevenueGrowthPerShare')
                            if eps_growth:
                                fundamentals['Crecimiento EPS 5Y (%)'] = eps_growth * 100
                        
                        if fundamentals['Crecimiento Ganancias LT (%)'] is None:
                            revenue_growth = growth_data.get('revenueGrowth')
                            if revenue_growth:
                                fundamentals['Crecimiento Ganancias LT (%)'] = revenue_growth * 100
                
                except Exception as e:
                    st.warning(f"⚠️ FMP API error para {ticker}")
            
            # 2. Intentar con Alpha Vantage como backup
            try:
                url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
                response = requests.get(url, timeout=10).json()
                
                if 'Symbol' in response:
                    # Completar datos faltantes con Alpha Vantage
                    if fundamentals['Margen Neto (%)'] is None:
                        profit_margin = response.get('ProfitMargin')
                        if profit_margin and profit_margin != 'None':
                            fundamentals['Margen Neto (%)'] = float(profit_margin) * 100
                    
                    if fundamentals['P/E Ratio'] is None:
                        pe_ratio = response.get('PERatio')
                        if pe_ratio and pe_ratio != 'None':
                            fundamentals['P/E Ratio'] = float(pe_ratio)
                    
                    if fundamentals['P/B Ratio'] is None:
                        pb_ratio = response.get('PriceToBookRatio')
                        if pb_ratio and pb_ratio != 'None':
                            fundamentals['P/B Ratio'] = float(pb_ratio)
                    
                    # Calcular ROIC con datos de Alpha Vantage si no se pudo antes
                    if fundamentals['ROIC (%)'] is None:
                        roe_av = response.get('ReturnOnEquityTTM')
                        debt_equity_av = response.get('DebtToEquityRatio')
                        if roe_av and debt_equity_av and roe_av != 'None' and debt_equity_av != 'None':
                            try:
                                roe_val = float(roe_av)
                                de_val = float(debt_equity_av)
                                total_capital_ratio = 1 / (1 + de_val)
                                fundamentals['ROIC (%)'] = roe_val * total_capital_ratio
                            except:
                                pass
                    
                    # Intentar obtener growth rates
                    if fundamentals['Crecimiento Ganancias LT (%)'] is None:
                        analyst_target = response.get('AnalystTargetPrice')
                        current_price = response.get('Price')
                        if analyst_target and current_price and analyst_target != 'None' and current_price != 'None':
                            try:
                                # Aproximación muy básica basada en target price
                                target_val = float(analyst_target)
                                current_val = float(current_price)
                                implied_growth = ((target_val / current_val) - 1) * 100
                                if -50 <= implied_growth <= 100:  # Filtrar valores extremos
                                    fundamentals['Crecimiento Ganancias LT (%)'] = implied_growth
                            except:
                                pass
                        
            except Exception as e:
                st.warning(f"⚠️ Alpha Vantage no disponible para {ticker}")
            
            # 3. Intentar con Polygon.io para datos adicionales
            if POLYGON_API_KEY != "demo" and len([k for k, v in fundamentals.items() if v is None and k not in ['Name', 'Ticker']]) > 1:
                try:
                    # Polygon para datos financieros básicos
                    polygon_url = f"https://api.polygon.io/vX/reference/financials?ticker={ticker}&apikey={POLYGON_API_KEY}"
                    polygon_response = requests.get(polygon_url, timeout=10).json()
                    
                    if polygon_response.get('status') == 'OK' and polygon_response.get('results'):
                        financials = polygon_response['results'][0]  # Datos más recientes
                        
                        # Polygon tiene estructura diferente, ajustar según su documentación
                        # Esto es un ejemplo básico, necesitarías ajustar según la respuesta real
                        if 'financials' in financials:
                            fin_data = financials['financials']
                            
                            # Intentar extraer ratios si están disponibles
                            if 'balance_sheet' in fin_data and 'income_statement' in fin_data:
                                try:
                                    # Cálculos básicos con datos de Polygon si están disponibles
                                    pass  # Implementar según estructura de respuesta
                                except:
                                    pass
                
                except Exception as e:
                    st.warning(f"⚠️ Polygon API error para {ticker}")
        
        
        return fundamentals
        
    except Exception as e:
        st.error(f"❌ Error al obtener datos para {ticker}: {str(e)}")
        return None

# Función mejorada para mostrar indicadores con explicación de datos faltantes
def display_indicator_card_improved(label, value, threshold_good=None, threshold_bad=None, is_percentage=True, higher_is_better=True, explanation=None):
    """Mostrar indicador mejorado con explicaciones"""
    if value is None:
        value_display = "N/A"
        color = "#666666"
        if explanation:
            tooltip = f"💡 {explanation}"
        else:
            tooltip = "💡 Dato no disponible en APIs gratuitas"
    else:
        value_display = f"{value:.2f}{'%' if is_percentage else ''}"
        tooltip = ""
        if threshold_good is not None and threshold_bad is not None:
            if higher_is_better:
                if value >= threshold_good:
                    color = "#2ecc71"
                    tooltip = "✅ Excelente"
                elif value <= threshold_bad:
                    color = "#e74c3c"
                    tooltip = "❌ Preocupante"
                else:
                    color = "#f1c40f"
                    tooltip = "⚠️ Aceptable"
            else:
                if value <= threshold_good:
                    color = "#2ecc71"
                    tooltip = "✅ Excelente"
                elif value >= threshold_bad:
                    color = "#e74c3c"
                    tooltip = "❌ Alto"
                else:
                    color = "#f1c40f"
                    tooltip = "⚠️ Moderado"
        else:
            color = "#1f77b4"
    
    st.markdown(f"""
    <div class='indicator-card' title='{tooltip}'>
        <div class='indicator-label'>{label}</div>
        <div class='indicator-value' style='color: {color}'>{value_display}</div>
        {f"<div style='font-size: 0.7rem; color: #888;'>{tooltip}</div>" if tooltip else ""}
    </div>
    """, unsafe_allow_html=True)

# NUEVA SECCIÓN PARA "EXPLORAR EMPRESA" (reemplaza la existente):
with mode_tab2:
    st.subheader("🔎 Explorar Empresa")
    
    ticker_input = st.text_input("Ingresa el ticker (ej. AAPL, MSFT)", max_chars=10).upper()
    
    if st.button("🔍 Analizar Empresa"):
        if ticker_input:
            with st.spinner("Obteniendo datos fundamentales..."):
                fundamentals = get_fundamental_data(ticker_input)
                
                if fundamentals:
                    # Obtener información adicional de la empresa
                    try:
                        stock = yf.Ticker(ticker_input)
                        info = stock.info
                        company_name = fundamentals['Name']
                    except:
                        company_name = ticker_input
                    
                    st.success(f"✅ Análisis completado")
                    
                    # Mostrar información básica
                    st.markdown(f"### {company_name} ({ticker_input})")
                    
                    # Advertencia sobre datos limitados
                    st.info("💡 **Nota**: Algunos indicadores pueden no estar disponibles con APIs gratuitas. Los datos faltantes se marcan como 'N/A'.")
                    
                    # Mostrar indicadores en tarjetas mejoradas
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Rentabilidad**")
                        display_indicator_card_improved("Margen Neto", fundamentals['Margen Neto (%)'], 10, 0)
                        display_indicator_card_improved(
                            "ROIC", 
                            fundamentals['ROIC (%)'], 
                            20, 5,
                            explanation="Calculado aproximadamente. Para datos precisos consultar reportes financieros."
                        )
                    
                    with col2:
                        st.markdown("**Crecimiento**")
                        display_indicator_card_improved("Crecimiento EPS 5Y", fundamentals['Crecimiento EPS 5Y (%)'], 10, 0)
                        display_indicator_card_improved(
                            "Crecimiento Ganancias LT", 
                            fundamentals['Crecimiento Ganancias LT (%)'], 
                            8, 0,
                            explanation="Datos limitados en APIs gratuitas. Consultar análisis de analistas."
                        )
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        st.markdown("**Evaluación**")
                        display_indicator_card_improved("P/E Ratio", fundamentals['P/E Ratio'], 15, 30, is_percentage=False, higher_is_better=False)
                        display_indicator_card_improved("P/B Ratio", fundamentals['P/B Ratio'], 2, 5, is_percentage=False, higher_is_better=False)
                    
                    with col4:
                        st.markdown("**Deuda**")
                        display_indicator_card_improved("Ratio Liquidez Inmediata", fundamentals['Ratio Liquidez Inmediata'], 1, 0.5, is_percentage=False)
                        display_indicator_card_improved("Ratio Deuda/Patrimonio", fundamentals['Ratio Deuda/Patrimonio'], 0.5, 1, is_percentage=False, higher_is_better=False)
                    
                    col5, col6 = st.columns(2)
                    with col5:
                        st.markdown("**Dividendos**")
                        display_indicator_card_improved("Rentabilidad Dividendo", fundamentals['Rentabilidad Dividendo (%)'], 3, 0)
                        display_indicator_card_improved("Ratio Reparto Dividendos", fundamentals['Ratio Reparto Dividendos (%)'], 30, 70, higher_is_better=False)
                    
                    # Sección de recomendaciones para datos faltantes
                    with st.expander("📚 ¿Dónde encontrar los datos faltantes?"):
                        st.markdown("""
                        **Para obtener datos más precisos y completos:**
                        
                        🔸 **ROIC**: Reportes anuales 10-K, calculadoras financieras como Morningstar
                        🔸 **Crecimiento LT**: Estimaciones de analistas en Yahoo Finance, Bloomberg, Reuters
                        🔸 **Datos históricos**: SEC EDGAR, reportes trimestrales de la empresa
                        🔸 **APIs premium**: Financial Modeling Prep, Quandl, Polygon.io
                        
                        **Sitios web gratuitos recomendados:**
                        - Yahoo Finance (sección Analysts)
                        - MarketWatch 
                        - Seeking Alpha
                        - Morningstar (versión gratuita)
                        """)
                        
                else:
                    st.error(f"❌ No se encontraron datos para {ticker_input}. Verifica que el ticker sea válido y esté listado en mercados principales.")
        else:
            st.warning("⚠️ Por favor, ingresa un ticker válido.")

# Sidebar con información adicional
with st.sidebar:
    st.markdown("### ℹ️ Información del Sistema")
    
    # Estadísticas rápidas
    total_ops = len(st.session_state.operations)
    unique_tickers = st.session_state.operations['ticker'].nunique() if not st.session_state.operations.empty else 0
    
    st.info(f"📊 **Operaciones registradas:** {total_ops}")
    st.info(f"🎯 **Tickers únicos:** {unique_tickers}")
    
    # Botón de actualización
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        st.session_state.operations = load_operations()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🛠️ Acciones Rápidas")
    
    if st.button("💾 Backup de Operaciones"):
        if not st.session_state.operations.empty:
            backup_name = f"backup_operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            st.session_state.operations.to_csv(backup_name, index=False)
            st.success(f"✅ Backup creado: {backup_name}")
        else:
            st.warning("⚠️ No hay operaciones para respaldar")