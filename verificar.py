

import numpy as np
import matplotlib.pyplot as plt

from serial import (
    simular_carga_serial,
    simular_descarga_serial
)


# Parámetros del modelo
Vs = 5.0
V_inicial = 5.0
dt = 0.001
tiempo_final = 11.75

n_pasos = int(round(tiempo_final / dt))
tiempo = np.arange(n_pasos + 1) * dt


# Tres circuitos de prueba
R = np.array([1000.0, 3000.0, 5000.0])
C = np.array([100e-6, 220e-6, 470e-6])

indice_curva = 0


# Resultados numéricos mediante Euler
finales_carga, curva_carga = simular_carga_serial(
    R, C, Vs, dt, n_pasos, indice_curva
)

finales_descarga, curva_descarga = simular_descarga_serial(
    R, C, V_inicial, dt, n_pasos, indice_curva
)


# Soluciones analíticas para los voltajes finales
carga_exacta_final = Vs * (1 - np.exp(-tiempo_final / (R * C)))

descarga_exacta_final = V_inicial * np.exp(
    -tiempo_final / (R * C)
)


# Soluciones analíticas para el circuito seleccionado
R_curva = R[indice_curva]
C_curva = C[indice_curva]

curva_carga_exacta = Vs * (
    1 - np.exp(-tiempo / (R_curva * C_curva))
)

curva_descarga_exacta = V_inicial * np.exp(
    -tiempo / (R_curva * C_curva)
)


# Calcular errores absolutos
error_carga = np.abs(curva_carga - curva_carga_exacta)
error_descarga = np.abs(curva_descarga - curva_descarga_exacta)

error_final_carga = np.abs(finales_carga - carga_exacta_final)
error_final_descarga = np.abs(
    finales_descarga - descarga_exacta_final
)


# Mostrar resultados
print("VERIFICACIÓN DEL MÉTODO DE EULER")
print("--------------------------------")

print("\nVoltajes finales de carga:")
print("Euler:    ", finales_carga)
print("Analítico:", carga_exacta_final)

print("\nVoltajes finales de descarga:")
print("Euler:    ", finales_descarga)
print("Analítico:", descarga_exacta_final)

print("\nError absoluto máximo en la curva de carga:")
print(np.max(error_carga), "V")

print("\nError absoluto máximo en la curva de descarga:")
print(np.max(error_descarga), "V")

print("\nError absoluto en voltajes finales de carga:")
print(error_final_carga)

print("\nError absoluto en voltajes finales de descarga:")
print(error_final_descarga)


# Criterio de verificación basado en el voltaje de la fuente
tolerancia_absoluta = 0.002 * Vs

error_maximo_carga = np.max(error_carga)
error_maximo_descarga = np.max(error_descarga)

carga_correcta = error_maximo_carga <= tolerancia_absoluta

descarga_correcta = error_maximo_descarga <= tolerancia_absoluta

print("\nTolerancia absoluta permitida:")
print(tolerancia_absoluta, "V")

print("\n¿La curva de carga cumple el criterio?", carga_correcta)
print("¿La curva de descarga cumple el criterio?", descarga_correcta)

print("\n¿La curva de carga cumple la tolerancia?", carga_correcta)
print("¿La curva de descarga cumple la tolerancia?", descarga_correcta)


# Gráficas: Euler frente a solución analítica
fig, ejes = plt.subplots(2, 1, figsize=(10, 8))

ejes[0].plot(tiempo, curva_carga, label="Euler")
ejes[0].plot(
    tiempo,
    curva_carga_exacta,
    "--",
    label="Solución analítica"
)
ejes[0].set_title("Verificación de la carga del circuito RC")
ejes[0].set_xlabel("Tiempo (s)")
ejes[0].set_ylabel("Voltaje (V)")
ejes[0].grid(True)
ejes[0].legend()

ejes[1].plot(tiempo, curva_descarga, label="Euler")
ejes[1].plot(
    tiempo,
    curva_descarga_exacta,
    "--",
    label="Solución analítica"
)
ejes[1].set_title("Verificación de la descarga del circuito RC")
ejes[1].set_xlabel("Tiempo (s)")
ejes[1].set_ylabel("Voltaje (V)")
ejes[1].grid(True)
ejes[1].legend()

plt.tight_layout()
plt.show()
