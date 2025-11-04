import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="📈 Calculadora de Inversión",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📈 Calculadora de Inversión a Largo Plazo")
st.markdown("---")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración de Inversión")

# Parámetros de inversión
initial_investment = st.sidebar.number_input(
    "💰 Inversión Inicial ($)", 
    min_value=0.0, 
    value=1000.0, 
    step=100.0,
    help="Cantidad inicial que vas a invertir"
)

periodic_investment = st.sidebar.number_input(
    "📅 Inversión Periódica ($)", 
    min_value=0.0, 
    value=230.0, 
    step=10.0,
    help="Cantidad que invertirás cada período"
)

investment_frequency = st.sidebar.selectbox(
    "🔄 Frecuencia de Inversión",
    options=[1, 2, 3, 6, 12],
    index=1,  # Default: cada 2 meses
    format_func=lambda x: f"Cada {x} mes{'es' if x > 1 else ''}",
    help="Cada cuántos meses harás la inversión periódica"
)

annual_return = st.sidebar.slider(
    "📊 Rendimiento Anual Esperado (%)", 
    min_value=1.0, 
    max_value=25.0, 
    value=8.0, 
    step=0.1,
    help="Rendimiento anual esperado de tu portafolio"
) / 100

investment_years = st.sidebar.slider(
    "📅 Años de Inversión", 
    min_value=1, 
    max_value=40, 
    value=20,
    help="Por cuántos años mantendrás la inversión"
)

# Sección de activos sugeridos
st.sidebar.markdown("---")
st.sidebar.header("💡 Rendimientos Históricos de Referencia")
st.sidebar.markdown("""
**Conservador (3-6%)**
- Bonos del tesoro
- CDs, Fondos de renta fija

**Moderado (6-10%)**
- S&P 500 (VOO, SPY)
- Índices diversificados

**Agresivo (10%+)**
- Acciones individuales
- ETFs de crecimiento
- Crypto (muy volátil)

**Tu portafolio actual:**
- MSFT, AAPL, VISA, VOO
- Rendimiento esperado: 7-10%
""")

# Función principal de cálculo
@st.cache_data
def calculate_investment(initial, periodic, frequency, annual_ret, years):
    monthly_return = (1 + annual_ret) ** (1/12) - 1
    total_months = years * 12
    
    results = []
    current_value = 0
    total_invested = 0
    
    for month in range(total_months + 1):
        # Determinar inversión del mes
        if month == 0:
            monthly_investment = initial
        elif month % frequency == 0:
            monthly_investment = periodic
        else:
            monthly_investment = 0
        
        # Actualizar totales
        total_invested += monthly_investment
        current_value += monthly_investment
        
        # Aplicar rendimiento mensual (excepto el primer mes)
        if month > 0:
            current_value *= (1 + monthly_return)
        
        profit = current_value - total_invested
        
        results.append({
            'Mes': month,
            'Año': month // 12,
            'Inversión_Mensual': monthly_investment,
            'Inversión_Acumulada': total_invested,
            'Valor_Portafolio': current_value,
            'Ganancia_Acumulada': profit,
            'ROI_Porcentaje': (profit / total_invested * 100) if total_invested > 0 else 0
        })
    
    return pd.DataFrame(results)

# Calcular los datos
df = calculate_investment(
    initial_investment, 
    periodic_investment, 
    investment_frequency, 
    annual_return, 
    investment_years
)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

final_data = df.iloc[-1]

with col1:
    st.metric(
        "💰 Total Invertido", 
        f"${final_data['Inversión_Acumulada']:,.0f}",
        help="Suma de todas tus inversiones"
    )

with col2:
    st.metric(
        "📈 Valor Final", 
        f"${final_data['Valor_Portafolio']:,.0f}",
        help="Valor total de tu portafolio al final"
    )

with col3:
    st.metric(
        "🎯 Ganancia Total", 
        f"${final_data['Ganancia_Acumulada']:,.0f}",
        help="Dinero ganado por los rendimientos"
    )

with col4:
    st.metric(
        "🚀 ROI Total", 
        f"{final_data['ROI_Porcentaje']:.0f}%",
        help="Retorno sobre la inversión"
    )

st.markdown("---")

# Tabs para diferentes vistas
tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "📋 Tabla Detallada", "🔍 Análisis"])

with tab1:
    st.subheader("Crecimiento del Portafolio")
    
    # Gráfico principal
    fig = go.Figure()
    
    # Filtrar datos para el gráfico (cada año)
    yearly_data = df[df['Mes'] % 12 == 0].copy()
    
    fig.add_trace(go.Scatter(
        x=yearly_data['Año'],
        y=yearly_data['Valor_Portafolio'],
        mode='lines+markers',
        name='Valor del Portafolio',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=yearly_data['Año'],
        y=yearly_data['Inversión_Acumulada'],
        mode='lines+markers',
        name='Total Invertido',
        line=dict(color='#A23B72', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Evolución de la Inversión a lo Largo del Tiempo",
        xaxis_title="Años",
        yaxis_title="Valor ($)",
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de barras por año
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ganancia por Año")
        yearly_profit = yearly_data.copy()
        yearly_profit['Ganancia_Anual'] = yearly_profit['Ganancia_Acumulada'].diff().fillna(0)
        
        fig_bar = px.bar(
            yearly_profit[1:], 
            x='Año', 
            y='Ganancia_Anual',
            title="Ganancia Generada Cada Año",
            color='Ganancia_Anual',
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("Distribución Final")
        final_distribution = pd.DataFrame({
            'Concepto': ['Inversión Total', 'Ganancias'],
            'Valor': [final_data['Inversión_Acumulada'], final_data['Ganancia_Acumulada']]
        })
        
        fig_pie = px.pie(
            final_distribution, 
            values='Valor', 
            names='Concepto',
            title="Composición del Portafolio Final",
            color_discrete_sequence=['#A23B72', '#2E86AB']
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Tabla Detallada de la Inversión")
    
    # Selector de vista
    view_option = st.selectbox(
        "Selecciona la vista:",
        ["Cada 2 años", "Anual", "Cada 6 meses", "Mensual"]
    )
    
    # Filtrar datos según la vista seleccionada
    if view_option == "Cada 2 años":
        filtered_df = df[df['Mes'] % 24 == 0].copy()
    elif view_option == "Anual":
        filtered_df = df[df['Mes'] % 12 == 0].copy()
    elif view_option == "Cada 6 meses":
        filtered_df = df[df['Mes'] % 6 == 0].copy()
    else:  # Mensual
        filtered_df = df.copy()
    
    # Calcular ganancia del período
    filtered_df['Ganancia_Periodo'] = filtered_df['Ganancia_Acumulada'].diff().fillna(0)
    filtered_df['Inversión_Periodo'] = filtered_df['Inversión_Acumulada'].diff().fillna(initial_investment)
    
    # Preparar tabla para mostrar
    display_df = filtered_df[['Año', 'Inversión_Periodo', 'Inversión_Acumulada', 
                             'Valor_Portafolio', 'Ganancia_Periodo', 'Ganancia_Acumulada']].copy()
    
    # Formatear números
    for col in ['Inversión_Periodo', 'Inversión_Acumulada', 'Valor_Portafolio', 
                'Ganancia_Periodo', 'Ganancia_Acumulada']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    
    # Renombrar columnas
    display_df.columns = ['Año', 'Inversión del Período', 'Inversión Acumulada', 
                         'Valor del Portafolio', 'Ganancia del Período', 'Ganancia Acumulada']
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Botón para descargar CSV
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Descargar datos como CSV",
        data=csv,
        file_name=f"inversion_proyeccion_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("🔍 Análisis de tu Inversión")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Estadísticas Clave")
        
        monthly_avg_gain = (final_data['Valor_Portafolio'] - initial_investment) / (investment_years * 12)
        yearly_avg_gain = monthly_avg_gain * 12
        
        st.write(f"**Ganancia promedio mensual:** ${monthly_avg_gain:,.0f}")
        st.write(f"**Ganancia promedio anual:** ${yearly_avg_gain:,.0f}")
        st.write(f"**Inversión total:** ${final_data['Inversión_Acumulada']:,.0f}")
        st.write(f"**Múltiplo de inversión:** {final_data['Valor_Portafolio'] / final_data['Inversión_Acumulada']:.1f}x")
        
        # Tiempo para duplicar inversión
        double_investment = final_data['Inversión_Acumulada'] * 2
        years_to_double = None
        for _, row in df.iterrows():
            if row['Valor_Portafolio'] >= double_investment:
                years_to_double = row['Año']
                break
        
        if years_to_double:
            st.write(f"**Años para duplicar inversión:** {years_to_double}")
    
    with col2:
        st.markdown("### 💡 Comparación de Escenarios")
        
        scenarios = {
            "Conservador (5%)": 0.05,
            "Tu escenario actual": annual_return,
            "Optimista (12%)": 0.12,
            "Muy optimista (15%)": 0.15
        }
        
        scenario_results = []
        for name, rate in scenarios.items():
            scenario_df = calculate_investment(
                initial_investment, periodic_investment, 
                investment_frequency, rate, investment_years
            )
            final_value = scenario_df.iloc[-1]['Valor_Portafolio']
            scenario_results.append({
                'Escenario': name,
                'Rendimiento': f"{rate*100:.1f}%",
                'Valor Final': f"${final_value:,.0f}"
            })
        
        scenario_comparison = pd.DataFrame(scenario_results)
        st.dataframe(scenario_comparison, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Recomendaciones")
    
    if annual_return <= 0.06:
        st.info("💡 **Portafolio Conservador**: Considera agregar algunos ETFs de crecimiento para mejorar rendimientos.")
    elif annual_return <= 0.10:
        st.success("✅ **Portafolio Balanceado**: Buen equilibrio entre riesgo y rendimiento.")
    else:
        st.warning("⚠️ **Portafolio Agresivo**: Asegúrate de estar cómodo con la volatilidad que esto implica.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<p>📈 Calculadora de Inversión | Creada con Streamlit</p>
<p><small>⚠️ Esta calculadora es solo para fines educativos. Las inversiones pasadas no garantizan rendimientos futuros.</small></p>
</div>
""", unsafe_allow_html=True)