# Calculadora clínica de polisomnografía pediátrica

Versión hospitalaria premium en Streamlit para generar un reporte clínico estructurado de polisomnografía pediátrica, con descarga en PDF y Word editable.

## Funcionalidades

- Entrada manual de parámetros principales de polisomnografía pediátrica.
- Interpretación automática de:
  - IAH pediátrico
  - oxigenación nocturna
  - eficiencia del sueño
  - índice de arousal
  - PLMI
  - predominio REM
  - patrón posicional
- Reporte clínico estructurado sin identificación del paciente.
- Descarga en:
  - PDF
  - Word editable (.docx)

## Archivos

```text
polisomnografia-pediatrica-app-premium/
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

1. Suba estos archivos a GitHub.
2. Ingrese a Streamlit Community Cloud.
3. Seleccione **New app**.
4. Elija su repositorio.
5. Configure:
   - Branch: `main`
   - Main file path: `app.py`
6. Presione **Deploy**.

## Umbrales usados para IAH pediátrico

- Normal: <1 evento/hora
- Leve: 1 a <5 eventos/hora
- Moderada: 5 a <10 eventos/hora
- Severa: >=10 eventos/hora

## Nota clínica

La interpretación automática es un apoyo para estructurar el reporte. La interpretación final debe integrarse con edad, síntomas, comorbilidades, examen físico, indicación del estudio y criterios vigentes del laboratorio de sueño.
