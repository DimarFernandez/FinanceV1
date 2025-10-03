import streamlit as st
import pandas as pd
import os
import joblib
import openpyxl

# --- Configuration ---
MODEL_DIR = "models" # Directory where your .pkl models are stored
PREDEFINED_MODELS = {
    
    "Portfolio: L2-ALL": "lstm_entity_1.0_p1.0.keras",
    "Portfolio: L2B": "lstm_entity_3.0_p3.0.keras",
    "Portfolio LJL: ": "lstm_entity_4.0_p4.0.keras",
    
}

# --- Function to load a model ---
@st.cache_resource # Cache the model loading to avoid reloading on every rerun
def load_model(model_name):
    model_path = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(model_path):
        st.error(f"Error: El archivo del modelo '{model_name}' no se encontró en '{MODEL_DIR}'.")
        return None
    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"Error al cargar el modelo '{model_name}': {e}")
        return None

# --- Streamlit Application Layout ---
st.set_page_config(
    page_title="Aplicación de Predicción  Financiera con Modelos ",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("📊 Aplicación de Predicción Financiera con Modelos")
st.markdown("---")

# Sidebar for model selection
st.sidebar.header("Selección de Modelo y Carga de Datos")

# Model selection combo box
selected_model_display_name = st.sidebar.selectbox(
    "Selecciona un modelo:",
    list(PREDEFINED_MODELS.keys())
)

# Get the actual filename for the selected model
selected_model_filename = PREDEFINED_MODELS[selected_model_display_name]

# File uploader
uploaded_file = st.sidebar.file_uploader(
    "Sube tu archivo Excel (.xlsx o .xls):",
    type=["xlsx", "xls"]
)

st.sidebar.markdown("---")

# Main content area
st.header(f"Modelo Seleccionado: {selected_model_display_name}")

if uploaded_file is not None:
    st.success("Archivo Excel cargado exitosamente.")
    try:
        # Read the Excel file
        df = pd.read_excel(uploaded_file)
        #st.subheader("Vista previa de los datos cargados:")
        #st.dataframe(df.head())

        # Load the selected model
        model = load_model(selected_model_filename)

        if model is not None:
            st.subheader("Ejecutando el modelo...")
            try:
                prediction_result = model.predict(df)
                st.subheader("Resultado de la predicción (Primeros 12 meses):")

                if not isinstance(prediction_result, pd.Series):
                    prediction_series = pd.Series(prediction_result)
                else:
                    prediction_series = prediction_result

                first_12_predictions = prediction_series.head(12)

                month_names = [
                    "01", "02", "03", "04", "05", "06",
                    "07", "08", "09", "10", "11", "12"
                ]

                num_predictions_to_show = len(first_12_predictions)
                display_month_names = month_names[:num_predictions_to_show]

                # --- START OF MODIFICATION ---
                # Generate month numbers (1 to num_predictions_to_show)
                month_numbers = list(range(1, num_predictions_to_show + 1))

                prediction_df = pd.DataFrame({
                    "Número de Mes": month_numbers, # Added month number
                    "Mes": display_month_names,
                    "Predicción": first_12_predictions.values
                })
                # --- END OF MODIFICATION ---

                #st.dataframe(prediction_df)

                # --- Add the chart here ---
                # st.subheader("Gráfico de Predicciones Mensuales:")
                # You can choose to set index by "Mes" or "Número de Mes"
                # If you want the chart to order by month number, even if names are shown:
                st.bar_chart(prediction_df.set_index("Mes"))
                # If you want to use "Número de Mes" directly on the axis (might not show names):
                # st.bar_chart(prediction_df.set_index("Número de Mes"))


            except Exception as e:
                st.error(f"Error al ejecutar el modelo con los datos proporcionados: {e}")
                st.info("Asegúrate de que tus datos de entrada coincidan con lo que el modelo espera.")
        else:
            st.warning("No se pudo cargar el modelo seleccionado. Por favor, verifica la ruta y el archivo.")

    except Exception as e:
        st.error(f"Error al leer el archivo Excel o al procesar los datos: {e}")
else:
    st.info("Por favor, selecciona un modelo y sube un archivo Excel para comenzar.")

st.markdown("---")
st.caption("Desarrollado con Streamlit y Python.")