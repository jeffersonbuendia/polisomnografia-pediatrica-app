# Calculadora clínica de polisomnografía pediátrica

App en Streamlit para generar un reporte clínico automatizado de polisomnografía pediátrica con descarga en PDF.

## Funcionalidades

- Entrada manual de valores principales de PSG pediátrica.
- Clasificación automática del IAH pediátrico.
- Interpretación automática de oxigenación, eficiencia del sueño, arousals, PLMI, patrón REM y patrón posicional.
- Generación de impresión clínica integrada.
- Descarga del reporte en PDF.

## Estructura del repositorio

```text
polisomnografia-pediatrica-app/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Community Cloud

1. Suba estos archivos a un repositorio de GitHub.
2. Ingrese a Streamlit Community Cloud.
3. Seleccione **New app**.
4. Elija el repositorio.
5. Configure:
   - Branch: `main`
   - Main file path: `app.py`
6. Presione **Deploy**.

## Nota clínica

La app usa umbrales pediátricos habituales para IAH:
- Normal: <1 evento/hora
- Leve: 1 a <5 eventos/hora
- Moderada: 5 a <10 eventos/hora
- Severa: >=10 eventos/hora

La interpretación final debe integrarse con edad, síntomas, comorbilidades, examen físico y criterios vigentes del laboratorio de sueño.
