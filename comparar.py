
import numpy as np

from serial import (
    simular_carga_serial,
    simular_descarga_serial
)

from paralelo import (
    simular_carga_paralela,
    simular_descarga_paralela
)


# Parámetros
Vs = 5.0
dt = 0.001
tiempo_final = 11.75

n_pasos = int(round(tiempo_final / dt))

R = np.array([1000.0, 3000.0, 5000.0])
C = np.array([100e-6, 220e-6, 470e-6])

indice_curva = 0


# Ejecutar carga serial y paralela
carga_serial, curva_carga_serial = simular_carga_serial(
    R, C, Vs, dt, n_pasos, indice_curva
)

carga_paralela, curva_carga_paralela = simular_carga_paralela(
    R, C, Vs, dt, n_pasos, indice_curva
)


# Ejecutar descarga serial y paralela
descarga_serial, curva_descarga_serial = simular_descarga_serial(
    R, C, Vs, dt, n_pasos, indice_curva
)

descarga_paralela, curva_descarga_paralela = simular_descarga_paralela(
    R, C, Vs, dt, n_pasos, indice_curva
)


# Comparar los resultados
print("COMPARACIÓN SERIAL VS PARALELO")
print("--------------------------------")

print(
    "Voltajes finales de carga:",
    np.allclose(carga_serial, carga_paralela)
)

print(
    "Curvas de carga:",
    np.allclose(curva_carga_serial, curva_carga_paralela)
)

print(
    "Voltajes finales de descarga:",
    np.allclose(descarga_serial, descarga_paralela)
)

print(
    "Curvas de descarga:",
    np.allclose(curva_descarga_serial, curva_descarga_paralela)
)
