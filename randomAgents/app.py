# simulación 1: visualización de roomba individual que limpia tiles sucias
# autor: Luis Emilio Veledíaz Flores - A01029829
# fecha: 19 de Noviembre de 2025

from random_agents.agent import RandomAgent, DirtCell, ChargingStation, ObstacleAgent
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle
import solara


def roombaPortrayal(agent):
    """
    define la representación visual de cada agente.
    parámetros:
        agent: agente a representar
    retorna: estilo de representación del agente
    """
    if agent is None:
        return  # no dibuja si no hay agente

    # crea un estilo de representación base
    portrayal = AgentPortrayalStyle(
        size=100,
        marker="s",
    )

    # asigna color y propiedades según el tipo de agente
    if isinstance(agent, RandomAgent):
        portrayal.color = "red"  # roomba es rojo
        portrayal.zorder = 3  # se dibuja encima
    elif isinstance(agent, DirtCell):
        portrayal.zorder = 0  # se dibuja al fondo
        if agent.isDirty:
            portrayal.color = "tab:brown"  # tile sucia es cafecito
            portrayal.size = 100
        else:
            portrayal.color = "white"  # tile limpia es blanca
            portrayal.size = 0  # no se ve
    elif isinstance(agent, ChargingStation):
        portrayal.color = "tab:green"  # cargador es verde
        portrayal.zorder = 2
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "black"  # obstáculo es negro
        portrayal.zorder = 1

    return portrayal  # retorna el estilo del agente


# parámetros del modelo que se pueden ajustar en la interfaz
modelParams = {
    "seed": {
        "type": "InputText",
        "value": 50,
        "label": "Random Seed",
    },
    "width": Slider("Grid Width", 20, 10, 30),  # ancho del grid
    "height": Slider("Grid Height", 20, 10, 30),  # alto del grid
    "dirtyPercentage": Slider("Dirty Cells (%)", 30, 0, 100),  # porcentaje de suciedad
    "obstaclePercentage": Slider("Obstacles (%)", 15, 0, 100),  # porcentaje de obstáculos
    "maxSteps": Slider("Max Steps", 10000, 1000, 100000),  # límite máximo de pasos
}


def postProcessSpace(ax):
    """ajusta el aspecto del espacio visual."""
    ax.set_aspect("equal")  # asegura que el grid sea cuadrado


def postProcessLines(ax):
    """ajusta el aspecto de los gráficos de líneas."""
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))


# componente que visualiza el grid con los agentes
spaceComponent = make_space_component(
    roombaPortrayal,  # función que define cómo se ven los agentes
    draw_grid=False,  # no dibuja líneas de grid
    post_process=postProcessSpace,  # aplica ajustes visuales
)

# componente que visualiza gráficos de líneas con datos del modelo
plotComponent = make_plot_component(
    {"Movement Count": "tab:blue", "Step Limit": "tab:red", "Percentage Clean": "tab:green", "Battery": "tab:orange"},
    post_process=postProcessLines,  # aplica ajustes visuales
)


def metricsComponent(model):
    """
    muestra las estadísticas de la simulación.
    parámetros:
        model: modelo de la simulación
    retorna: componente markdown con las métricas
    """
    # obtiene las métricas del modelo
    metrics = model.getMetrics()
    
    # obtiene el agente roomba
    agent = model.agents_by_type[RandomAgent][0] if len(model.agents_by_type[RandomAgent]) > 0 else None

    # retorna un texto con las estadísticas
    return solara.Markdown(f"""
### Estadísticas

- **Tiempo total:** {model.steps} pasos
-   **Tiempo hasta limpiar todo:** {metrics['timeAllClean']} pasos
- **Porcentaje de limpieza:** {metrics['percentageClean']:.2f}%
-   **Número de movimientos:** {metrics['movementCount']}
- **Batería restante:** {agent.battery if agent else 0}%
""")

# crea la instancia del modelo
model = RandomModel()

# crea la página de visualización con todos los componentes
page = SolaraViz(
    model,
    components=[spaceComponent, plotComponent, metricsComponent],  # componentes a mostrar
    model_params=modelParams,  # parámetros
    name="Simulación de Roomba Individual - A01029829",  # nombre de la simulación
)