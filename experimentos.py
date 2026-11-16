# Experimentos de la actividad de aspiradoras: varia el numero de agentes y genera tablas y graficas.
# Autores: Valeria Giselle Portilla Robles A01752371 
# 		   Gilberto de Jesús Marcos Orozco A01801865
# Fecha: 16/11/2026

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from model import ModeloLimpieza

ANCHO_HABITACION = 20
ALTO_HABITACION = 20
PORCENTAJE_SUCIAS = 30
TIEMPO_MAXIMO = 10000
REPETICIONES = 100
NUMEROS_AGENTES = [1, 2, 3, 5, 10, 20, 30, 50, 100]


# Corre una simulacion completa y regresa las tres estadisticas pedidas.
# numeroAgentes: cantidad de aspiradoras.
# semilla: semilla del generador aleatorio.
# Regresa un diccionario con tiempo, porcentajeLimpias, movimientos e historial de limpieza.
def ejecutarSimulacion(numeroAgentes, semilla):
	modelo = ModeloLimpieza(ANCHO_HABITACION, ALTO_HABITACION, numeroAgentes,
		PORCENTAJE_SUCIAS, TIEMPO_MAXIMO, semilla)
	while not modelo.haTerminado():
		modelo.step()
	return {
		"tiempo": modelo.steps,
		"porcentajeLimpias": modelo.porcentajeLimpias,
		"movimientos": modelo.contarMovimientos(),
		"historial": modelo.datos.get_model_vars_dataframe()["porcentajeLimpias"].tolist(),
	}


# Corre todas las repeticiones para cada cantidad de agentes.
# Regresa una tabla con una fila por corrida.
def correrExperimentos():
	filas = []
	for numeroAgentes in NUMEROS_AGENTES:
		for repeticion in range(REPETICIONES):
			resultado = ejecutarSimulacion(numeroAgentes, repeticion)
			filas.append({
				"agentes": numeroAgentes,
				"tiempo": resultado["tiempo"],
				"porcentajeLimpias": resultado["porcentajeLimpias"],
				"movimientos": resultado["movimientos"],
			})
	return pd.DataFrame(filas)


# Calcula promedio y desviacion estandar de cada metrica por cantidad de agentes.
# corridas: tabla con una fila por corrida.
# Regresa la tabla resumen.
def resumirCorridas(corridas):
	resumen = corridas.groupby("agentes").agg(
		tiempoPromedio=("tiempo", "mean"),
		tiempoDesviacion=("tiempo", "std"),
		limpiasPromedio=("porcentajeLimpias", "mean"),
		movimientosPromedio=("movimientos", "mean"),
		movimientosDesviacion=("movimientos", "std"),
	)
	resumen["movimientosPorAgente"] = resumen["movimientosPromedio"] / resumen.index
	resumen["agentesPorTiempo"] = resumen.index * resumen["tiempoPromedio"]
	return resumen


# Dibuja una grafica de promedio con banda de desviacion contra el numero de agentes.
# resumen: tabla resumen por cantidad de agentes.
# columnaPromedio, columnaDesviacion: columnas a graficar.
# titulo, etiquetaY, archivo: textos y nombre del archivo de salida.
def graficarMetrica(resumen, columnaPromedio, columnaDesviacion, titulo, etiquetaY, archivo):
	figura, eje = plt.subplots(figsize=(6, 4))
	promedio = resumen[columnaPromedio]
	eje.plot(resumen.index, promedio, marker="o", color="#1f4e79")
	if columnaDesviacion is not None:
		eje.fill_between(resumen.index, promedio - resumen[columnaDesviacion],
			promedio + resumen[columnaDesviacion], alpha=0.2, color="#1f4e79")
	eje.set_xscale("log")
	eje.set_xticks(resumen.index)
	eje.set_xticklabels(resumen.index)
	eje.set_xlabel("Número de agentes (escala logarítmica)")
	eje.set_ylabel(etiquetaY)
	eje.set_title(titulo)
	eje.grid(alpha=0.3)
	figura.tight_layout()
	figura.savefig(archivo, dpi=200)
	plt.close(figura)


# Dibuja el porcentaje de celdas limpias a lo largo del tiempo para varias cantidades de agentes.
# Regresa nada, guarda la figura en disco.
def graficarAvance():
	figura, eje = plt.subplots(figsize=(6, 4))
	for numeroAgentes in [1, 5, 20, 100]:
		resultado = ejecutarSimulacion(numeroAgentes, 0)
		eje.plot(resultado["historial"], label=str(numeroAgentes) + (" agente" if numeroAgentes == 1 else " agentes"))
	eje.set_xscale("symlog", linthresh=10)
	eje.set_xlabel("Paso de tiempo")
	eje.set_ylabel("Celdas limpias (%)")
	eje.set_title("Avance de la limpieza (semilla 0)")
	eje.legend()
	eje.grid(alpha=0.3)
	figura.tight_layout()
	figura.savefig("avance_limpieza.png", dpi=200)
	plt.close(figura)


# Punto de entrada: corre experimentos, guarda tablas y genera todas las graficas.
def principal():
	corridas = correrExperimentos()
	resumen = resumirCorridas(corridas)
	corridas.to_csv("corridas.csv", index=False)
	resumen.to_csv("resumen.csv")
	graficarMetrica(resumen, "tiempoPromedio", "tiempoDesviacion",
		"Tiempo hasta limpiar todo", "Pasos de tiempo", "tiempo_vs_agentes.png")
	graficarMetrica(resumen, "movimientosPromedio", "movimientosDesviacion",
		"Movimientos totales de los agentes", "Movimientos", "movimientos_vs_agentes.png")
	graficarMetrica(resumen, "agentesPorTiempo", None,
		"Costo total: agentes por pasos de tiempo", "Agentes × pasos", "costo_vs_agentes.png")
	graficarAvance()
	print(resumen.round(2).to_string())
	print("Corridas que no terminaron:", int((corridas["porcentajeLimpias"] < 100).sum()))


if __name__ == "__main__":
	principal()
