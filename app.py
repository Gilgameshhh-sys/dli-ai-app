import streamlit as st
import openai
import json
import re  # Para validar emails

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DLI-AI Risk Audit", page_icon="🛡️", layout="centered")

# --- ESTILOS "CONVERSIÓN" (BOTONES DE PAGO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    .stSelectbox, .stNumberInput, .stTextInput, div[data-baseweb="select"] > div { 
        background-color: #F0F2F6; color: black; 
    }
    p, h1, h2, h3, label, li { color: black !important; }
    
    /* Botón Principal (Calcular) */
    div.stButton > button { 
        background-color: #2e2e2e; color: white; border: none; width: 100%; padding: 10px; font-weight: bold; 
    }
    
    /* Estilo para caja de resultados */
    .result-box {
        padding: 20px; border-radius: 10px; background-color: #ffe6e6; border: 2px solid #ff4b4b; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.title("🛡️ DLI-AI | Auditoría de Riesgo")
st.markdown("### Descubre cuánto te costaría un incidente informático hoy.")

# --- FORMULARIO DE DATOS ---
col1, col2 = st.columns(2)
with col1:
    rubro = st.selectbox("1. Rubro", ["Estudio Jurídico", "PyME Tech", "Salud", "Comercio", "Industria"])
    empleados = st.number_input("Cantidad de Empleados", min_value=1, value=5)
with col2:
    moneda = st.radio("Moneda", ["ARS", "USD"])
    facturacion = st.number_input("Facturación Mensual", min_value=0, value=1000000)

st.write("---")
st.subheader("🕵️ Análisis de Vulnerabilidad")

q1 = st.selectbox("3. Dispositivos (BYOD)", 
                  ["Todo corporativo (Seguro)", "Híbrido", "Personal / Sin control (Alto Riesgo)"])
q2 = st.selectbox("4. Backups", 
                  ["Automatizados y probados", "Manuales / A veces", "No existen / Nunca probados"])
q3 = st.selectbox("5. Control de Accesos", 
                  ["Tengo control total", "Accesos compartidos", "Dependo 100% de un externo"])

st.write("---")
st.subheader("📧 Tu Informe")

# --- CAPTURA DE EMAIL (EL GATE) ---
email = st.text_input("Ingresa tu email corporativo para recibir el diagnóstico:", placeholder="nombre@tuempresa.com")

def validar_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

boton = st.button("🚨 CALCULAR RIESGO AHORA")

# --- LÓGICA ---
if boton:
    if not email or not validar_email(email):
        st.error("⚠️ Por favor, ingresa un email válido para ver los resultados.")
    elif "OPENAI_API_KEY" not in st.secrets:
        st.error("❌ Error: Falta configurar la API Key en Secrets.")
    else:
        # Aquí "GUARDAMOS" el lead (Por ahora lo imprimimos en la consola del servidor)
        print(f"NUEVO LEAD CAPTURADO: {email} - Rubro: {rubro}")
        
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        
        with st.spinner('Auditando vectores de ataque y calculando impacto financiero...'):
            try:
                # Prompt enfocado en vender la solución
                prompt = f"""
                Actúa como DLI-AI. Calcula riesgo para: {rubro}, Fac: {facturacion} {moneda}.
                Vulns: {q1}, {q2}, {q3}.
                
                Responde JSON:
                {{
                    "monto": "$ [MONTO REALISTA]",
                    "mensaje": "[FRASE DE MIEDO PROFESIONAL]",
                    "fragilidad": [0-100],
                    "solucion_preview": "Detectamos 3 fallos críticos en tu esquema de seguridad que garantizan una pérdida de datos en menos de 12 meses."
                }}
                """
                
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.choices[0].message.content.replace("```json", "").replace("```", "")
                data = json.loads(content)
                
                # --- PANTALLA DE RESULTADOS (EL GANCHO) ---
                st.markdown(f"""
                <div class="result-box">
                    <h2 style="color: #cc0000; margin:0;">PÉRDIDA ESTIMADA: {data['monto']}</h2>
                    <p style="font-size: 18px; font-weight: bold;">{data['mensaje']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_metrica1, col_metrica2 = st.columns(2)
                col_metrica1.metric("Índice de Fragilidad", f"{data['fragilidad']}%")
                col_metrica2.error("Nivel de Riesgo: CRÍTICO")
                
                st.write("---")
                st.info(f"🔍 **Diagnóstico Preliminar:** {data['solucion_preview']}")
                
                # --- LA VENTA (EL COBRO) ---
                st.subheader("🛡️ ¿Cómo evitar perder este dinero?")
                st.write("Hemos generado tu **Plan de Blindaje IT Personalizado** que incluye:")
                st.write("✅ Protocolo Anti-Ransomware para tus empleados.")
                st.write("✅ Guía paso a paso de Backups Inmutables (Costo $0).")
                st.write("✅ Checklist legal para evitar multas.")
                
                # --- BOTÓN DE MERCADOPAGO ---
                # ¡¡¡PEGA TU LINK DE MERCADOPAGO AQUÍ ABAJO!!!
                link_mercadopago = "https://mpago.la/2D7W7LL" 
                
                st.link_button(f"🔓 DESBLOQUEAR SOLUCIÓN Y PLAN DE ACCIÓN", link_mercadopago)
                st.caption("🔒 Pago seguro vía MercadoPago. Recibirás el plan en tu email en 24hs.")

            except Exception as e:
                st.error(f"Error: {e}")
