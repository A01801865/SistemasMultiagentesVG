# Agentes de la simulacion de aspiradoras: la celda de la habitacion y la aspiradora con arquitectura de subsuncion.
# Autores: Valeria Giselle Portilla Robles A01752371 
# 		   Gilberto de Jesús Marcos Orozco A01801865
# Fecha: 16/11/2026

import solara
from mesa.visualization import SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.utils import update_counter
import mesa.visualization.solara_viz as moduloVisualizacion
from solara.lab import theme

from agents import Celda, AgenteAspiradora
from model import ModeloLimpieza

# Colores de la interfaz: azul como base, turquesa como secundario y ambar para la suciedad
COLOR_PRINCIPAL = "#1565C0"
COLOR_SECUNDARIO = "#00ACC1"
COLOR_CELDA_LIMPIA = "#E3F2FD"
COLOR_CELDA_SUCIA = "#F9A825"
COLOR_ASPIRADORA = "#0D47A1"
COLOR_BORDE = "#1565C0"

# Estilo general de la pagina (CSS): fondo, barra superior, tarjetas, botones y sliders
ESTILO_PAGINA = """
body, .v-application {
	font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
	background: linear-gradient(160deg, #EAF3FF 0%, #F6FAFF 55%, #E3F7FA 100%) !important;
}
.v-app-bar, .v-toolbar, header.v-toolbar {
	background: linear-gradient(90deg, #0B3C8A 0%, #1565C0 55%, #00ACC1 100%) !important;
	color: #FFFFFF !important;
	box-shadow: 0 4px 14px rgba(11, 60, 138, 0.35) !important;
}
.v-toolbar-title, .v-toolbar__title {
	font-weight: 600 !important;
	letter-spacing: 0.5px !important;
}
.v-navigation-drawer {
	background: #F3F8FF !important;
	border-right: 1px solid #C9DDF5 !important;
}
.v-card {
	background: #FFFFFF !important;
	border-radius: 16px !important;
	border-top: 4px solid #1565C0 !important;
	box-shadow: 0 6px 18px rgba(21, 101, 192, 0.12) !important;
}
.v-card-title, .v-card__title {
	color: #0B3C8A !important;
	font-weight: 600 !important;
}
.v-btn.bg-primary, .v-btn--variant-elevated.bg-primary, .v-btn.primary {
	background: linear-gradient(135deg, #1565C0, #1E88E5) !important;
	color: #FFFFFF !important;
	border-radius: 10px !important;
	box-shadow: 0 3px 8px rgba(21, 101, 192, 0.35) !important;
}
.v-slider-track__fill, .v-slider-thumb__surface, .v-selection-control--dirty .v-selection-control__input {
	background-color: #1976D2 !important;
	color: #1976D2 !important;
}
.v-tab, .v-tab--selected {
	color: #0B3C8A !important;
}
.v-tabs-slider, .v-tab__slider {
	background-color: #00ACC1 !important;
}
img {
	max-height: 350px !important;
	max-width: 100% !important;
	width: auto !important;
	height: auto !important;
	object-fit: contain !important;
	display: block !important;
	margin: 0 auto !important;
}
"""

theme.themes.light.primary = COLOR_PRINCIPAL
theme.themes.light.secondary = COLOR_SECUNDARIO
theme.themes.dark.primary = "#42A5F5"
theme.themes.dark.secondary = COLOR_SECUNDARIO


# Define como se dibuja cada agente: celdas como cuadros y aspiradoras como circulos azul oscuro.
# agente: agente a dibujar.
# Regresa el estilo de dibujo del agente.
def retratarAgente(agente):
	if isinstance(agente, Celda):
		color = COLOR_CELDA_SUCIA if agente.estaSucia else COLOR_CELDA_LIMPIA
		return AgentPortrayalStyle(color=color, marker="s", size=250, zorder=1)
	return AgentPortrayalStyle(color=COLOR_ASPIRADORA, marker="o", size=90, zorder=10)


# Ajusta la figura para que las celdas se vean cuadradas y sin ejes.
# ax: ejes de matplotlib donde se dibuja la habitacion.
def postProcesar(ax):
	ax.set_aspect("equal")
	ax.set_xticks([])
	ax.set_yticks([])
	for borde in ax.spines.values():
		borde.set_color(COLOR_BORDE)
		borde.set_linewidth(2.0)


parametrosModelo = {
	"rng": {
		"type": "SliderInt",
		"value": 42,
		"label": "Random Seed",
		"min": 0,
		"max": 1000,
		"step": 1,
	},
	"ancho": {
		"type": "SliderInt",
		"value": 20,
		"label": "Ancho (M)",
		"min": 5,
		"max": 40,
		"step": 1,
	},
	"alto": {
		"type": "SliderInt",
		"value": 20,
		"label": "Alto (N)",
		"min": 5,
		"max": 40,
		"step": 1,
	},
	"numeroAgentes": {
		"type": "SliderInt",
		"value": 5,
		"label": "Numero de agentes",
		"min": 1,
		"max": 100,
		"step": 1,
	},
	"porcentajeSucias": {
		"type": "SliderInt",
		"value": 30,
		"label": "Celdas sucias al inicio (%)",
		"min": 0,
		"max": 100,
		"step": 1,
	},
	"tiempoMaximo": {
		"type": "SliderInt",
		"value": 1000,
		"label": "Tiempo maximo (pasos)",
		"min": 100,
		"max": 10000,
		"step": 100,
	},
}

# Muestra los contadores dentro de la seccion Information de la barra lateral.
@solara.component
def mostrarInformacion(model):
	update_counter.get()
	numeroAgentes = len(model.agents_by_type[AgenteAspiradora])
	movimientos = model.contarMovimientos()
	promedio = movimientos / numeroAgentes if numeroAgentes else 0
	solara.Text(f"Pasos transcurridos: {model.steps}")
	solara.Text(f"Movimientos totales: {movimientos}")
	solara.Text(f"Movimientos promedio por agente: {promedio:.2f}")


# Sustituye solo el contenido del panel Information de SolaraViz.
moduloVisualizacion.ShowSteps = mostrarInformacion


# Crea la instancia inicial del modelo
modelo1 = ModeloLimpieza()

renderizador = SpaceRenderer(modelo1, backend="matplotlib").setup_agents(retratarAgente)
renderizador.render()
renderizador.post_process = postProcesar

# Pagina de la aplicacion: aplica el estilo y muestra SolaraViz. Solara busca este componente por el nombre Page.
@solara.component
def Page():
	solara.Style(ESTILO_PAGINA)
	SolaraViz(
		modelo1,
		renderizador,
		model_params=parametrosModelo,
		name="Agentes Aspiradoras",
	)