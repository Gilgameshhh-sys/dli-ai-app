import streamlit as st
import openai
import json
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# --- CONFIGURACIÓN DE PÁGINA (WIDE MODE PARA DASHBOARD) ---
st.set_page_config(page_title="DLI-AI | Enterprise Risk Audit", page_icon="🛡️", layout="centered")

# --- ESTILOS CSS PROFESIONALES ---
st.markdown("""
    <style>
    /* Fondo limpio */
    .stApp { background-color: #f8f9fa; color: #212529; }
    
    /* Headers */
    h1 { color: #0f172a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    h2, h3 { color: #334155; }
    
    /* Cajas de métricas */
    div[data-testid="stMetricValue"] { font-size: 28px; color: #dc2626; font-weight: bold; }
    
    /* Botón Principal */
    div.stButton > button { 
        background-color: #0f172a; color: white; border-radius: 8px; 
        padding: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;
        border: 2px solid #0f172a; transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: white; color: #0f172a; border: 2px solid #0f172a;
    }
    
    /* Inputs */
    .stSelectbox, .stNumberInput, .stTextInput { border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES (GRÁFICOS Y PDF) ---

def crear_gauge_chart(score):
    """Crea un gráfico de velocímetro para el riesgo"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Índice de Fragilidad Digital", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#dc2626"}, # Rojo alarma
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#e2e8f0'},
                {'range': [50, 80], 'color': '#fca5a5'},
                {'range': [80, 100], 'color': '#fecaca'}],
        }))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

def crear_chart_comparativo(perdida_estimada, costo_solucion):
    """Crea un gráfico de barras comparando el desastre vs la prevención"""
    fig = go.Figure(data=[
        go.Bar(name='Costo del Desastre', x=['Impacto Financiero'], y=[perdida_estimada], marker_color='#dc2626'),
        go.Bar(name='Inversión en Blindaje', x=['Costo Prevención'], y=[costo_solucion], marker_color='#16a34a')
    ])
    fig.update_layout(
        title="ROI de la Seguridad (Costo vs Prevención)",
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Monto Estimado",
        height=300
    )
    return fig

def generar_pdf(empresa, rubro, data_json):
    """Genera un reporte PDF simple en memoria"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(40, 10, f"REPORTE DE RIESGO DLI-AI: {empresa.upper()}")
    pdf.ln(20)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Fecha de Auditoria: Generado automaticamente", ln=True)
    pdf.cell(0, 10, f"Rubro Analizado: {rubro}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(220, 53, 69) # Rojo
    pdf.cell(0, 10, f"PERDIDA ESTIMADA: {data_json['monto']}", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "DIAGNOSTICO DE IA:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, data_json['mensaje'])
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "PLAN DE ACCION RECOMENDADO:", ln=True)
    for tip in data_json.get('tips', []):
        pdf.cell(0, 10, f"- {tip}", ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ PRINCIPAL ---

st.markdown("<div style='text-align: center; padding-bottom: 20px;'><h1 style='font-size: 50px;'>🛡️ DLI-AI</h1><p style='color:gray;'>Data Loss Impact Intelligence System v3.0</p></div>", unsafe_allow_html=True)

with st.expander("ℹ️ ¿Cómo funciona este sistema?", expanded=False):
    st.write("DLI-AI utiliza algoritmos de riesgo financiero basados en ISO 27001 para estimar el impacto monetario de un incidente de ciberseguridad en tiempo real.")

# --- DATOS DEL CLIENTE ---
st.subheader("1. Perfil de la Organización")
col1, col2 = st.columns(2)
with col1:
    empresa_nombre = st.text_input("Nombre de la Empresa (Opcional)", placeholder="Ej: Perez & Asoc.")
    rubro = st.selectbox("Industria / Rubro", ["Estudio Jurídico", "PyME Tech", "Salud / Clínica", "Comercio / Retail", "Finanzas"])
    empleados = st.number_input("Cantidad de Empleados", min_value=1, value=10)
with col2:
    moneda = st.radio("Moneda de Análisis", ["USD (Dólares)", "ARS (Pesos)"])
    facturacion = st.number_input("Facturación Mensual Aprox.", min_value=0, value=5000000)

st.write("---")
st.subheader("2. Matriz de Vulnerabilidad")

col_q1, col_q2, col_q3 = st.columns(3)
with col_q1:
    st.markdown("**📱 Dispositivos (BYOD)**")
    q1 = st.selectbox("Uso de equipos personales", ["Prohibido (Seguro)", "Híbrido / A veces", "Total (Alto Riesgo)"], label_visibility="collapsed")
with col_q2:
    st.markdown("**💾 Política de Backups**")
    q2 = st.selectbox("Estado de copias", ["Probados mensual", "Manual / Sin probar", "Inexistentes"], label_visibility="collapsed")
with col_q3:
    st.markdown("**🔑 Gestión de Accesos**")
    q3 = st.selectbox("Control de usuarios", ["MFA / Gestor Claves", "Claves compartidas", "Sin control"], label_visibility="collapsed")

st.write("---")

# --- BOTÓN DE ACCIÓN ---
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    boton_calcular = st.button("🚨 EJECUTAR AUDITORÍA FINANCIERA")

# --- LÓGICA DE PROCESAMIENTO ---
if boton_calcular:
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("❌ Error Crítico: API Key no configurada en Secrets.")
    else:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        
        # Animación Pro
        msg_placeholder = st.empty()
        msg_placeholder.info("🔄 Iniciando motor de análisis de riesgos...")
        
        try:
            # Prompt avanzado
            prompt = f"""
            Actúa como Auditor Senior de Ciberseguridad DLI-AI.
            Analiza: {rubro}, {empleados} empleados, Factura {facturacion} {moneda}.
            Vulnerabilidades: {q1}, {q2}, {q3}.
            
            Calcula:
            1. 'monto': Perdida financiera total estimada (Downtime + Multas + Recuperación). Sé realista pero severo.
            2. 'monto_num': El número entero del monto (ej: 5000000).
            3. 'mensaje': Explicación ejecutiva de 2 lineas del por qué de ese monto.
            4. 'fragilidad': 0 a 100.
            5. 'tips': 3 acciones técnicas concretas y cortas.
            
            Responde JSON estricto.
            """
            
            response = openai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
            data = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
            
            msg_placeholder.empty() # Limpiar mensaje de carga
            
            # --- DASHBOARD DE RESULTADOS ---
            st.success("✅ AUDITORÍA COMPLETADA EXITOSAMENTE")
            
            # 1. KPIs Principales
            kpi1, kpi2 = st.columns([2, 1])
            with kpi1:
                st.metric("PÉRDIDA FINANCIERA ESTIMADA (Riesgo Inminente)", data['monto'], delta="- Impacto Negativo", delta_color="inverse")
            with kpi2:
                # Aquí podrías poner otra métrica
                st.metric("Nivel de Alerta", "CRÍTICO", delta="Inaceptable", delta_color="inverse")

            # 2. Gráficos Interactivos (Plotly)
            chart1, chart2 = st.columns(2)
            with chart1:
                # Velocímetro
                st.plotly_chart(crear_gauge_chart(data['fragilidad']), use_container_width=True)
            with chart2:
                # Comparativa (Precio ancla: Solución vale el 1% del problema)
                costo_solucion_aprox = data['monto_num'] * 0.05 # Asumimos que la solución cuesta el 5% del problema
                st.plotly_chart(crear_chart_comparativo(data['monto_num'], costo_solucion_aprox), use_container_width=True)

            # 3. Análisis Cualitativo
            st.error(f"📋 **Diagnóstico:** {data['mensaje']}")
            
            # 4. Generación de PDF en tiempo real
            pdf_bytes = generar_pdf(empresa_nombre or "Su Empresa", rubro, data)
            
            st.write("---")
            st.subheader("📂 Entregables y Siguientes Pasos")
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                # Botón de Descarga PDF Gratis (Lead Magnet)
                st.download_button(
                    label="📥 Descargar Reporte Oficial (PDF)",
                    data=pdf_bytes,
                    file_name="Reporte_Riesgo_DLI_AI.pdf",
                    mime="application/pdf"
                )
            
            with col_d2:
                # Upsell (Venta)
                link_pago = "https://mpago.la/2D7W7LL" # ¡PON TU LINK!
                st.link_button("🛡️ IMPLEMENTAR BLINDAJE AHORA", link_pago)
                st.caption("Obtén el manual de implementación y soporte técnico.")

        except Exception as e:
            st.error(f"Error en el análisis: {e}")
