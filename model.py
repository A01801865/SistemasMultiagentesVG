# Modelo de la simulacion de aspiradoras reactivas en una habitacion de MxN celdas.
# Autores: Valeria Giselle Portilla Robles A01752371 
# 		   Gilberto de Jesús Marcos Orozco A01801865
# Fecha: 16/11/2026

from mesa import DataCollector, Model
from mesa.discrete_space import OrthogonalMooreGrid

from agents import AgenteAspiradora, Celda

# Celda [1,1] del enunciado, que en coordenadas desde cero es (0, 0)
COORDENADA_INICIAL = (0, 0)


class ModeloLimpieza(Model):
	"""Habitacion de MxN celdas con celdas sucias al azar y aspiradoras que parten de [1,1]."""

	# Prepara la habitacion, las celdas sucias aleatorias y los agentes en la celda [1,1].
	# ancho, alto: dimensiones M y N de la habitacion.
	# numeroAgentes: cantidad de aspiradoras.
	# porcentajeSucias: porcentaje (0 a 100) de celdas sucias al inicio.
	# tiempoMaximo: maximo de pasos de tiempo que puede durar la simulacion.
	# rng: semilla del generador aleatorio para poder repetir una corrida.
	def __init__(self, ancho=20, alto=20, numeroAgentes=5, porcentajeSucias=30, tiempoMaximo=1000, rng=None):
		super().__init__(rng=rng)
		self.tiempoMaximo = tiempoMaximo
		self.totalCeldas = ancho * alto
		self.grid = OrthogonalMooreGrid((ancho, alto), torus=False, random=self.random)
		self.celdasPorCoordenada = {}
		self.cantidadSucias = 0
		self.crearCeldas(porcentajeSucias)
		self.crearAgentes(numeroAgentes)
		self.datos = DataCollector(model_reporters={"porcentajeLimpias": "porcentajeLimpias"})
		self.datos.collect(self)
		self.running = True

	# Coloca un agente Celda en cada posicion de la rejilla, algunas sucias al azar.
	# porcentajeSucias: porcentaje (0 a 100) de celdas que empiezan sucias.
	def crearCeldas(self, porcentajeSucias):
		cantidadInicial = round(self.totalCeldas * porcentajeSucias / 100)
		coordenadas = sorted(celda.coordinate for celda in self.grid.all_cells)
		coordenadasSucias = set(self.random.sample(coordenadas, cantidadInicial))
		for celda in self.grid.all_cells:
			estadoInicial = Celda.LIMPIA
			if celda.coordinate in coordenadasSucias:
				estadoInicial = Celda.SUCIA
			self.celdasPorCoordenada[celda.coordinate] = Celda(self, celda, estadoInicial)
		self.cantidadSucias = cantidadInicial

	# Crea las aspiradoras, todas en la celda inicial.
	# numeroAgentes: cantidad de agentes a crear.
	def crearAgentes(self, numeroAgentes):
		celdaInicial = self.celdasPorCoordenada[COORDENADA_INICIAL].cell
		for _ in range(numeroAgentes):
			AgenteAspiradora(self, celdaInicial)

	# Regresa el agente Celda de la coordenada dada, o None si queda fuera de la habitacion.
	# coordenada: tupla (x, y) a buscar.
	def obtenerCelda(self, coordenada):
		return self.celdasPorCoordenada.get(coordenada)

	# Descuenta una celda sucia del conteo del modelo.
	def restarSuciedad(self):
		self.cantidadSucias -= 1

	# Porcentaje de celdas limpias en este momento (0 a 100).
	@property
	def porcentajeLimpias(self):
		return 100 * (self.totalCeldas - self.cantidadSucias) / self.totalCeldas

	# Suma los movimientos hechos por todas las aspiradoras.
	def contarMovimientos(self):
		return sum(agente.movimientos for agente in self.agents_by_type[AgenteAspiradora])

	# Regresa True cuando ya no hay celdas sucias o se agoto el tiempo maximo.
	def haTerminado(self):
		return self.cantidadSucias == 0 or self.steps >= self.tiempoMaximo

	# Avanza un paso: activa a las aspiradoras en orden aleatorio y guarda el porcentaje de limpieza.
	def step(self):
		self.agents_by_type[AgenteAspiradora].shuffle_do("step")
		self.datos.collect(self)
		self.running = not self.haTerminado()
