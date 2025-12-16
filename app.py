import streamlit as st
import openai
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DLI-AI Risk Audit", page_icon="🛡️", layout="centered")

# --- CSS PARA ESTILO PROFESIONAL (MODO CLARO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    .stSelectbox, .stNumberInput, div[data-baseweb="select"] > div { background-color: #F0F2F6; color: black; }
    p, h1, h2, h3, label { color: black !important; }
    div.stButton > button { background-color: #ff4b4b; color: white; border: none; width: 100%; padding: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.title("🛡️ DLI-AI | Calculadora de Riesgo")
st.info("Sistema de Auditoría Financiera de Riesgo IT")

# --- FORMULARIO ---
col1, col2 = st.columns(2)
with col1:
    rubro = st.selectbox("1. Rubro", ["Estudio Jurídico", "PyME Tech", "Salud", "Comercio", "Industria"])
    empleados = st.number_input("Cantidad de Empleados", min_value=1, value=5)
with col2:
    moneda = st.radio("Moneda", ["ARS (Pesos)", "USD (Dólares)"])
    facturacion = st.number_input("Facturación Mensual", min_value=0, value=1000000)

st.write("---")
st.subheader("🔍 Diagnóstico de Vulnerabilidad")

q1 = st.selectbox("3. ¿Uso de Dispositivos Personales (BYOD)?", 
                  ["No, todo es corporativo y bloqueado", "Híbrido (algunos usan personal)", "Sí, todos usan su propio equipo (Alto Riesgo)"])

q2 = st.selectbox("4. ¿Estado de los Backups?", 
                  ["Automatizados y probados mensualmente", "Manuales / Nunca probados", "No tenemos backups centralizados"])

q3 = st.selectbox("5. ¿Si tu técnico de confianza desaparece hoy?", 
                  ["Tengo las claves y el control total", "Tengo las claves pero no sé usarlas", "Quedo totalmente bloqueado (Rehén)"])

boton = st.button("🚨 CALCULAR IMPACTO FINANCIERO")

# --- LÓGICA ---
if boton:
    # AQUÍ ESTÁ LA MAGIA: Buscamos la clave en los "Secretos" de Streamlit
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("❌ Error de Configuración: No se encontró la API Key en los secretos.")
    else:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        
        with st.spinner('Analizando vectores de ataque y calculando costos...'):
            try:
                prompt = f"""
                Actúa como DLI-AI. Calcula riesgo para: {rubro}, Empleados: {empleados}, Factura: {facturacion} {moneda}.
                Vulnerabilidades: {q1}, {q2}, {q3}.
                
                Responde SOLO un JSON válido con esta estructura exacta:
                {{
                    "monto": "$ [CALCULAR MONTO REALISTA BASADO EN FACTURACION]",
                    "mensaje": "[FRASE DE IMPACTO EMOCIONAL/FINANCIERO]",
                    "fragilidad": [NUMERO 0-100],
                    "tips": ["Tip 1 corto", "Tip 2 corto", "Tip 3 corto"]
                }}
                """
                
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.choices[0].message.content.replace("```json", "").replace("```", "")
                data = json.loads(content)
                
                st.success("✅ REPORTE GENERADO")
                st.metric(label="DINERO EN RIESGO INMEDIATO", value=data.get("monto"))
                st.error(f"⚠️ {data.get('mensaje')}")
                st.progress(data.get("fragilidad") / 100)
                st.caption(f"Nivel de Fragilidad Digital: {data.get('fragilidad')}%")
                
                st.subheader("🛡️ Plan de Acción Inmediato:")
                for tip in data.get("tips", []):
                    st.write(f"🔹 {tip}")
                    
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
