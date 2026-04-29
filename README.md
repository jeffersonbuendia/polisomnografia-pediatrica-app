# Calculadora clínica de polisomnografía pediátrica

Versión hospitalaria premium validada de una app en Streamlit para generar un reporte clínico estructurado de polisomnografía pediátrica, con descarga en PDF y Word editable.

## Funcionalidades

- Entrada manual de parámetros principales de polisomnografía pediátrica.
- Interpretación automática de:
  - IAH pediátrico
  - oxigenación nocturna
  - ODI3 u ODI4
  - eficiencia del sueño
  - índice de arousal con lenguaje orientativo
  - PLMI
  - predominio REM
  - patrón posicional
  - advertencia en menores de 2 años
- Reporte clínico estructurado sin identificación del paciente.
- Descarga en PDF y Word editable.

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

## Reglas clínicas incorporadas

### IAH pediátrico

- Normal: <1 evento/hora
- Leve: 1 a <5 eventos/hora
- Moderada: 5 a <10 eventos/hora
- Severa: >=10 eventos/hora

### ODI

- ODI4 >4 eventos/hora: anormal en niños mayores de 2 años
- ODI3 >7 eventos/hora: anormal en niños mayores de 2 años
- Menores de 2 años: requiere interpretación cautelosa

### Arousals

El índice de arousal se interpreta como orientativo porque no existe un punto de corte pediátrico universal único para definir severidad exclusivamente por este parámetro.

## Nota clínica

La interpretación automática es un apoyo para estructurar el reporte. La interpretación final debe integrarse con edad, síntomas, comorbilidades, examen físico, indicación del estudio y criterios vigentes del laboratorio de sueño.
