
import numpy as np
import matplotlib.pyplot as plt

from numba import njit, prange, get_num_threads


@njit(parallel=True)
def simular_carga_paralela(R, C, Vs, dt, n_pasos, indice_curva):
    
    "Simula la carga de varios capacitores RC. Distribuye los circuitos entre varios hilos usando prange"
    

    n_circuitos = len(R)

    voltajes_finales = np.empty(n_circuitos)
    curva = np.empty(n_pasos + 1)

    for i in prange(n_circuitos):

        vc = 0.0

        if i == indice_curva:
            curva[0] = vc

        for n in range(n_pasos):

            vc = vc + (dt / (R[i] * C[i])) * (Vs - vc)

            if i == indice_curva:
                curva[n + 1] = vc

        voltajes_finales[i] = vc

    return voltajes_finales, curva


@njit(parallel=True)
def simular_descarga_paralela(R, C, V_inicial, dt, n_pasos, indice_curva):
    
    "Simula la descarga de varios capacitores RC. Distribuye los circuitos entre varios hilos usando prange"  

    n_circuitos = len(R)

    voltajes_finales = np.empty(n_circuitos)
    curva = np.empty(n_pasos + 1)

    for i in prange(n_circuitos):

        vc = V_inicial

        if i == indice_curva:
            curva[0] = vc

        for n in range(n_pasos):

            vc = vc - (dt / (R[i] * C[i])) * vc

            if i == indice_curva:
                curva[n + 1] = vc

        voltajes_finales[i] = vc

    return voltajes_finales, curva


def graficar_resultados(tiempo, curva_carga, curva_descarga):
    
    "Genera las gráficas de carga y descarga del circuito RC"
    

    fig, ejes = plt.subplots(2, 1, figsize=(10, 8))

    ejes[0].plot(tiempo, curva_carga, label="Carga paralela")
    ejes[0].set_title("Proceso de carga del capacitor RC")
    ejes[0].set_xlabel("Tiempo (s)")
    ejes[0].set_ylabel("Voltaje del capacitor (V)")
    ejes[0].grid(True)
    ejes[0].legend()

    ejes[1].plot(tiempo, curva_descarga, label="Descarga paralela")
    ejes[1].set_title("Proceso de descarga del capacitor RC")
    ejes[1].set_xlabel("Tiempo (s)")
    ejes[1].set_ylabel("Voltaje del capacitor (V)")
    ejes[1].grid(True)
    ejes[1].legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    # Parámetros de simulación
    Vs = 5.0
    dt = 0.001
    tiempo_final = 11.75

    n_pasos = int(round(tiempo_final / dt))

    # Tres circuitos de prueba
    R = np.array([1000.0, 3000.0, 5000.0])
    C = np.array([100e-6, 220e-6, 470e-6])

    # Seleccionamos el primer circuito para visualizarlo
    indice_curva = 2

    # Consultar cantidad de hilos disponibles para Numba
    print("Hilos disponibles para Numba:", get_num_threads())

    # Simulación paralela de carga
    finales_carga, curva_carga = simular_carga_paralela(
        R, C, Vs, dt, n_pasos, indice_curva
    )

    # Simulación paralela de descarga
    finales_descarga, curva_descarga = simular_descarga_paralela(
        R, C, Vs, dt, n_pasos, indice_curva
    )

    # Eje temporal
    tiempo = np.arange(n_pasos + 1) * dt

    # Mostrar resultados
    print("\nSIMULACIÓN PARALELA DE CIRCUITOS RC")
    print("-----------------------------------")

    print("\nVoltajes finales durante la carga:")
    print(finales_carga)

    print("\nVoltajes finales durante la descarga:")
    print(finales_descarga)

    print("\nNúmero de instantes simulados:", len(tiempo))

    # Generar gráficas
    graficar_resultados(tiempo, curva_carga, curva_descarga)
