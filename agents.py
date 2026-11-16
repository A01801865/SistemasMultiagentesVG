# Agentes de la simulacion de aspiradoras: la celda de la habitacion y la aspiradora con arquitectura de subsuncion.
# Autores: Valeria Giselle Portilla Robles A01752371
# 		   Gilberto de Jesús Marcos Orozco A01801865
# Fecha: 16/11/2026

from mesa.discrete_space import CellAgent, FixedAgent

# Acciones posibles que producen los niveles de comportamiento
ACCION_ASPIRAR = "aspirar"
ACCION_MOVER = "mover"
ACCION_QUEDARSE = "quedarse"

# Las 8 direcciones posibles hacia las celdas vecinas (vecindad de Moore)
DIRECCIONES_VECINAS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class Celda(FixedAgent):
	"""Representa una celda LIMPIA o SUCIA de la habitacion."""

	LIMPIA = 0
	SUCIA = 1

	# Crea una celda en la posicion dada.
	# model: modelo al que pertenece.
	# cell: celda de la rejilla que ocupa.
	# estadoInicial: LIMPIA o SUCIA.
	def __init__(self, model, cell, estadoInicial=LIMPIA):
		super().__init__(model)
		self.cell = cell
		self.estado = estadoInicial

	# Regresa True si la celda tiene suciedad.
	@property
	def estaSucia(self):
		return self.estado == self.SUCIA

	# Deja la celda limpia y avisa al modelo para que actualice su conteo.
	def limpiar(self):
		self.estado = self.LIMPIA
		self.model.restarSuciedad()


class AgenteAspiradora(CellAgent):
	"""Aspiradora reactiva con arquitectura de subsuncion (Brooks, 1986).

	Tiene tres niveles de comportamiento que corren sin modelo del mundo:
	- Nivel 0, evitar paredes: es el nivel base. Filtra el movimiento final y si la
	  direccion sale de la habitacion, el agente se queda donde esta.
	- Nivel 1, vagar: propone moverse en una de las 8 direcciones al azar.
	- Nivel 2, limpiar: si la celda esta sucia, suprime la salida de vagar y aspira.
	"""

	# Crea una aspiradora y la coloca en la celda donde inicia.
	# model: modelo al que pertenece.
	# cell: celda de la rejilla donde empieza.
	def __init__(self, model, cell):
		super().__init__(model)
		self.cell = cell
		self.movimientos = 0

	# Ejecuta un paso de tiempo: percibe, deja que los niveles decidan y actua.
	def step(self):
		celdaActual = self.model.obtenerCelda(self.cell.coordinate)
		accion = self.decidirAccion(celdaActual.estaSucia)
		self.ejecutarAccion(accion, celdaActual)

	# Combina los niveles: limpiar suprime a vagar y evitar paredes filtra el resultado.
	# estaSucia: lectura del sensor de suciedad de la celda actual.
	# Regresa la accion final como una tupla (tipo, coordenada).
	def decidirAccion(self, estaSucia):
		accion = self.nivel2Limpiar(estaSucia)
		if accion is None:
			accion = self.nivel1Vagar()
		return self.nivel0EvitarParedes(accion)

	# Nivel 2: si hay suciedad, la salida es aspirar. Si no, no propone nada.
	# estaSucia: lectura del sensor de suciedad.
	# Regresa la accion de aspirar o None.
	def nivel2Limpiar(self, estaSucia):
		if estaSucia:
			return (ACCION_ASPIRAR, None)
		return None

	# Nivel 1: propone moverse a una de las 8 celdas vecinas elegida al azar.
	# Regresa la accion de mover con la coordenada destino.
	def nivel1Vagar(self):
		direccion = self.random.choice(DIRECCIONES_VECINAS)
		coordenadaX = self.cell.coordinate[0] + direccion[0]
		coordenadaY = self.cell.coordinate[1] + direccion[1]
		return (ACCION_MOVER, (coordenadaX, coordenadaY))

	# Nivel 0: deja pasar la accion, pero si es un movimiento fuera de la habitacion lo cambia por quedarse.
	# accion: accion propuesta por los niveles superiores.
	# Regresa la accion que realmente se va a ejecutar.
	def nivel0EvitarParedes(self, accion):
		if accion[0] == ACCION_MOVER and self.model.obtenerCelda(accion[1]) is None:
			return (ACCION_QUEDARSE, None)
		return accion

	# Realiza la accion elegida sobre la habitacion.
	# accion: tupla (tipo, coordenada).
	# celdaActual: agente Celda donde esta parado el agente.
	def ejecutarAccion(self, accion, celdaActual):
		if accion[0] == ACCION_ASPIRAR:
			celdaActual.limpiar()
		elif accion[0] == ACCION_MOVER:
			self.cell = self.model.obtenerCelda(accion[1]).cell
			self.movimientos += 1