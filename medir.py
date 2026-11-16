
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
import psutil

from pathlib import Path

from numba import get_num_threads, set_num_threads

from serial import (
    simular_carga_serial,
    simular_descarga_serial
)

from paralelo import (
    simular_carga_paralela,
    simular_descarga_paralela
)



# 1. CONFIGURACIÓN DEL EXPERIMENTO


Vs = 5.0
V_inicial = 5.0

dt = 0.001
tiempo_final = 11.75

n_pasos = int(round(tiempo_final / dt))

tamanos = [100, 500, 1000, 5000, 10000]

repeticiones = 15

semilla = 2026

# Carpetas de resultados
carpeta_resultados = Path("resultados")
carpeta_graficas = carpeta_resultados / "graficas_aleatorizadas"

carpeta_graficas.mkdir(parents=True, exist_ok=True)



# 2. INFORMACIÓN DEL EQUIPO


nucleos_fisicos = psutil.cpu_count(logical=False)
nucleos_logicos = psutil.cpu_count(logical=True)

max_hilos_numba = get_num_threads()

if nucleos_fisicos is None:
    nucleos_fisicos = max_hilos_numba

max_hilos = min(nucleos_fisicos, max_hilos_numba)

# Configuraciones de hilos: 1, 2, 4 y máximo disponible
hilos = []
cantidad = 1

while cantidad <= max_hilos:
    hilos.append(cantidad)
    cantidad *= 2

if max_hilos not in hilos:
    hilos.append(max_hilos)

hilos = sorted(set(hilos))


print("INFORMACIÓN DEL EQUIPO")
print("----------------------")
print("Núcleos físicos:", nucleos_fisicos)
print("Núcleos lógicos:", nucleos_logicos)
print("Máximo de hilos de Numba:", max_hilos_numba)
print("Configuraciones que se probarán:", hilos)



# 3. FUNCIONES DE SIMULACIÓN


def ejecutar_serial(R, C):
    
    "Ejecuta la carga y descarga de todos los circuitos utilizando la implementación serial."
    

    finales_carga, _ = simular_carga_serial(
        R, C, Vs, dt, n_pasos, -1
    )

    finales_descarga, _ = simular_descarga_serial(
        R, C, V_inicial, dt, n_pasos, -1
    )

    return finales_carga, finales_descarga


def ejecutar_paralelo(R, C):
    
    "Ejecuta la carga y descarga de todos los circuitos utilizando la implementación paralela."
    

    finales_carga, _ = simular_carga_paralela(
        R, C, Vs, dt, n_pasos, -1
    )

    finales_descarga, _ = simular_descarga_paralela(
        R, C, V_inicial, dt, n_pasos, -1
    )

    return finales_carga, finales_descarga



# 4. PREPARACIÓN Y COMPILACIÓN DE NUMBA


print("\nPreparando las funciones de Numba...")

R_prueba = np.array([1000.0, 3000.0, 5000.0])
C_prueba = np.array([100e-6, 220e-6, 470e-6])

# Compilar las funciones seriales
ejecutar_serial(R_prueba, C_prueba)

# Compilar las funciones paralelas con cada cantidad de hilos
for cantidad_hilos in hilos:

    set_num_threads(cantidad_hilos)

    ejecutar_paralelo(R_prueba, C_prueba)

print("Preparación terminada.")
print("La compilación inicial no se incluirá en las mediciones.")



# 5. ALMACENAMIENTO DE RESULTADOS


resultados = []

generador_orden = np.random.default_rng(semilla)



# 6. EXPERIMENTO DE RENDIMIENTO


for N in tamanos:

    print("\n====================================")
    print("SIMULANDO", N, "CIRCUITOS")
    print("====================================")

    # Generar parámetros reproducibles
    generador = np.random.default_rng(semilla + N)

    R = generador.uniform(1000.0, 5000.0, N)
    C = generador.uniform(100e-6, 470e-6, N)

    
    # 6.1. Verificación de resultados
    

    resultado_serial = ejecutar_serial(R, C)

    resultados_paralelos = {}

    for cantidad_hilos in hilos:

        set_num_threads(cantidad_hilos)

        resultado_paralelo = ejecutar_paralelo(R, C)

        resultados_paralelos[cantidad_hilos] = resultado_paralelo

        # Comparar carga
        carga_coincide = np.allclose(
            resultado_serial[0],
            resultado_paralelo[0],
            rtol=1e-10,
            atol=1e-12
        )

        # Comparar descarga
        descarga_coincide = np.allclose(
            resultado_serial[1],
            resultado_paralelo[1],
            rtol=1e-10,
            atol=1e-12
        )

        if not carga_coincide or not descarga_coincide:
            raise ValueError(
                "Los resultados seriales y paralelos no coinciden."
            )

    print("Verificación serial-paralela: correcta.")

    
    # 6.2. Construir lista de tareas
    

    tareas = [("serial", 1)]

    for cantidad_hilos in hilos:
        tareas.append(("paralela", cantidad_hilos))

    tiempos_por_configuracion = {
        tarea: [] for tarea in tareas
    }

    
    # 6.3. Realizar las repeticiones
    

    for repeticion in range(1, repeticiones + 1):

        # Copia de las tareas para esta repetición
        orden = tareas.copy()

        # Aleatorizar el orden
        generador_orden.shuffle(orden)

        print(
            "\nRepetición",
            repeticion,
            "de",
            repeticiones
        )

        for version, cantidad_hilos in orden:

            if version == "serial":

                inicio = time.perf_counter()

                ejecutar_serial(R, C)

                fin = time.perf_counter()

            else:

                set_num_threads(cantidad_hilos)

                inicio = time.perf_counter()

                ejecutar_paralelo(R, C)

                fin = time.perf_counter()

            tiempo_ejecucion = fin - inicio

            tiempos_por_configuracion[
                (version, cantidad_hilos)
            ].append(tiempo_ejecucion)

            resultados.append({
                "circuitos": N,
                "version": version,
                "hilos": cantidad_hilos,
                "repeticion": repeticion,
                "tiempo_s": tiempo_ejecucion
            })

    
    # 6.4. Mostrar resultados de este tamaño
    

    mediana_serial = np.median(
        tiempos_por_configuracion[("serial", 1)]
    )

    print("\nTiempo serial mediano:", mediana_serial, "s")

    for cantidad_hilos in hilos:

        tiempos = tiempos_por_configuracion[
            ("paralela", cantidad_hilos)
        ]

        mediana_paralela = np.median(tiempos)

        speedup = mediana_serial / mediana_paralela

        eficiencia = speedup / cantidad_hilos

        print(
            "Hilos:", cantidad_hilos,
            "| Tiempo:", round(mediana_paralela, 6),
            "| Speedup:", round(speedup, 4),
            "| Eficiencia:", round(eficiencia, 4)
        )



# 7. RESTABLECER HILOS


set_num_threads(max_hilos_numba)



# 8. GUARDAR MEDICIONES INDIVIDUALES


archivo_datos = (
    carpeta_resultados /
    "datos_rendimiento_aleatorizado.csv"
)

with open(
    archivo_datos,
    "w",
    newline="",
    encoding="utf-8"
) as archivo:

    campos = [
        "circuitos",
        "version",
        "hilos",
        "repeticion",
        "tiempo_s"
    ]

    escritor = csv.DictWriter(
        archivo,
        fieldnames=campos
    )

    escritor.writeheader()
    escritor.writerows(resultados)

print("\nMediciones guardadas en:", archivo_datos)



# 9. CALCULAR MEDIANAS Y DESVIACIONES


resumen = []

for N in tamanos:

    tiempos_seriales = [
        fila["tiempo_s"]
        for fila in resultados
        if fila["circuitos"] == N
        and fila["version"] == "serial"
    ]

    mediana_serial = np.median(tiempos_seriales)

    desviacion_serial = np.std(
        tiempos_seriales,
        ddof=1
    )

    resumen.append({
        "circuitos": N,
        "version": "serial",
        "hilos": 1,
        "mediana_s": mediana_serial,
        "desviacion_s": desviacion_serial,
        "speedup": 1.0,
        "eficiencia": 1.0
    })

    for cantidad_hilos in hilos:

        tiempos_paralelos = [
            fila["tiempo_s"]
            for fila in resultados
            if fila["circuitos"] == N
            and fila["version"] == "paralela"
            and fila["hilos"] == cantidad_hilos
        ]

        mediana_paralela = np.median(tiempos_paralelos)

        desviacion_paralela = np.std(
            tiempos_paralelos,
            ddof=1
        )

        speedup = mediana_serial / mediana_paralela

        eficiencia = speedup / cantidad_hilos

        resumen.append({
            "circuitos": N,
            "version": "paralela",
            "hilos": cantidad_hilos,
            "mediana_s": mediana_paralela,
            "desviacion_s": desviacion_paralela,
            "speedup": speedup,
            "eficiencia": eficiencia
        })



# 10. GUARDAR RESUMEN


archivo_resumen = (
    carpeta_resultados /
    "resumen_rendimiento_aleatorizado.csv"
)

with open(
    archivo_resumen,
    "w",
    newline="",
    encoding="utf-8"
) as archivo:

    campos = [
        "circuitos",
        "version",
        "hilos",
        "mediana_s",
        "desviacion_s",
        "speedup",
        "eficiencia"
    ]

    escritor = csv.DictWriter(
        archivo,
        fieldnames=campos
    )

    escritor.writeheader()
    escritor.writerows(resumen)

print("Resumen guardado en:", archivo_resumen)



# 11. GRÁFICA DE TIEMPO DE EJECUCIÓN


plt.figure(figsize=(10, 6))

for N in tamanos:

    filas = [
        fila for fila in resumen
        if fila["circuitos"] == N
        and fila["version"] == "paralela"
    ]

    tiempos = [fila["mediana_s"] for fila in filas]

    desviaciones = [
        fila["desviacion_s"] for fila in filas
    ]

    plt.errorbar(
        hilos,
        tiempos,
        yerr=desviaciones,
        marker="o",
        capsize=4,
        label=f"N = {N}"
    )

    tiempo_serial = next(
        fila["mediana_s"]
        for fila in resumen
        if fila["circuitos"] == N
        and fila["version"] == "serial"
    )

    plt.axhline(
        tiempo_serial,
        linestyle="--",
        alpha=0.35
    )

plt.xlabel("Cantidad de hilos")
plt.ylabel("Tiempo mediano (s)")
plt.title("Tiempo de ejecución según cantidad de hilos")
plt.xticks(hilos)
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    carpeta_graficas / "tiempo_ejecucion.png",
    dpi=300
)

plt.show()



# 12. GRÁFICA DE SPEEDUP


plt.figure(figsize=(10, 6))

for N in tamanos:

    filas = [
        fila for fila in resumen
        if fila["circuitos"] == N
        and fila["version"] == "paralela"
    ]

    valores = [fila["speedup"] for fila in filas]

    plt.plot(
        hilos,
        valores,
        marker="o",
        label=f"N = {N}"
    )

plt.plot(
    hilos,
    hilos,
    "--",
    label="Aceleración ideal"
)

plt.xlabel("Cantidad de hilos")
plt.ylabel("Speedup")
plt.title("Aceleración de la simulación RC")
plt.xticks(hilos)
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    carpeta_graficas / "speedup.png",
    dpi=300
)

plt.show()



# 13. GRÁFICA DE EFICIENCIA


plt.figure(figsize=(10, 6))

for N in tamanos:

    filas = [
        fila for fila in resumen
        if fila["circuitos"] == N
        and fila["version"] == "paralela"
    ]

    valores = [fila["eficiencia"] for fila in filas]

    plt.plot(
        hilos,
        valores,
        marker="o",
        label=f"N = {N}"
    )

plt.xlabel("Cantidad de hilos")
plt.ylabel("Eficiencia")
plt.title("Eficiencia de la paralelización")
plt.xticks(hilos)
plt.ylim(0, 1.05)
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    carpeta_graficas / "eficiencia.png",
    dpi=300
)

plt.show()



# 14. FINALIZACIÓN


print("\nEXPERIMENTO FINALIZADO")
print("----------------------")

print("Archivos generados:")
print(archivo_datos)
print(archivo_resumen)

print("\nGráficas:")
print(carpeta_graficas / "tiempo_ejecucion.png")
print(carpeta_graficas / "speedup.png")
print(carpeta_graficas / "eficiencia.png")
