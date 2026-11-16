# Simulación serial y paralela de circuitos RC

Proyecto de simulación de los procesos de carga y descarga de capacitores en circuitos RC, con comparación de una implementación serial y otra paralela mediante Python, Numba y `prange`.

## Contenido

- `serial.py`: implementación serial del método de Euler explícito.
- `paralelo.py`: implementación paralela; distribuye circuitos independientes con `prange`.
- `verificar.py`: compara la solución numérica de Euler con la solución analítica y calcula errores.
- `comparar.py`: compara resultados seriales y paralelos.
- `medir.py`: ejecuta las pruebas de rendimiento, guarda los CSV y genera las gráficas de tiempo, speedup y eficiencia.
- `datos/`: mediciones y resumen de la tercera ronda experimental.
- `graficas/`: figuras usadas en el informe.
- `informe/informe_RC.tex`: fuente LaTeX del informe. Las referencias bibliográficas quedan pendientes de la edición final del equipo.

## Requisitos

Se requiere Python 3 y las bibliotecas listadas en `requirements.txt`.

Instalación recomendada en un entorno virtual:

```bash
python -m venv .venv
```

Activación:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Orden recomendado de ejecución

Ejecutar desde la carpeta raíz `Proyecto_RC`.

1. Verificar el método numérico frente a la solución analítica:

```bash
python verificar.py
```

2. Comparar las implementaciones serial y paralela:

```bash
python comparar.py
```

3. Ejecutar una simulación serial ilustrativa:

```bash
python serial.py
```

4. Ejecutar una simulación paralela ilustrativa:

```bash
python paralelo.py
```

5. Ejecutar el experimento de rendimiento completo:

```bash
python medir.py
```

`medir.py` realiza calentamiento/compilación previa de las funciones Numba, excluye esa compilación de los intervalos medidos, verifica los resultados seriales y paralelos antes de medir cada tamaño, aleatoriza el orden de las configuraciones y realiza 15 repeticiones. El script genera una carpeta `resultados/` con los CSV y las gráficas nuevas.

## Parámetros principales

- Voltaje de fuente: 5 V.
- Resistencias: distribución uniforme entre 1000 y 5000 ohmios.
- Capacitancias: distribución uniforme entre 100 y 470 microfaradios.
- Paso temporal: 0.001 s.
- Tiempo final: 11.75 s.
- Tamaños: 100, 500, 1000, 5000 y 10000 circuitos.
- Repeticiones: 15.
- Semilla de generación: 2026 (la generación de parámetros usa `semilla + N` para cada tamaño).

La cantidad de hilos se determina dinámicamente a partir de los núcleos físicos disponibles y del máximo de hilos configurado en Numba. En el equipo de las mediciones reportadas se evaluaron 1, 2, 4 y 6 hilos.

## Resultados incluidos

Los archivos de `datos/` y `graficas/` corresponden a la ronda experimental cuyos resultados se reportan en el informe. Ejecutar nuevamente `medir.py` puede producir tiempos distintos, ya que dependen del equipo, del sistema operativo y de la carga del sistema.

## Registrar el entorno de ejecución

Para documentar el equipo en el que se reproduzcan las pruebas, ejecutar:

```bash
python --version
python -m pip show numpy numba matplotlib psutil
```

El modelo del procesador y el sistema operativo deben anotarse a partir del equipo utilizado. No se fijan aquí versiones ni un modelo de CPU que no hayan sido confirmados en esta entrega.

## Reproducir las figuras del informe

Al ejecutar `python medir.py`, las figuras de rendimiento se guardan en:

```text
resultados/graficas_aleatorizadas/
```

La figura de verificación carga/descarga se genera al ejecutar `python verificar.py` y se muestra en pantalla. Las imágenes entregadas en `graficas/` son las figuras conservadas de la ronda experimental del informe.

## Nota sobre el informe

El archivo LaTeX se incluye como fuente editable. El equipo debe completar y revisar las referencias bibliográficas antes de entregar la versión definitiva y compilar el PDF desde Overleaf o una instalación local de LaTeX.
