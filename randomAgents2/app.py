# simulación 2: visualización de múltiples roombas que se comunican y limpian tiles sucias
# autor: Luis Emilio Veledíaz Flores - A01029829
# fecha: 19 de Noviembre de 2025

from random_agents.agent import RandomAgent, DirtCell, ChargingStation, ObstacleAgent, Wall
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
        return

    portrayal = AgentPortrayalStyle(
        size=100,
        marker="s",
    )

    # asigna color y propiedades según el tipo de agente
    if isinstance(agent, RandomAgent):
        portrayal.color = "red"  # todos los roombas son rojos
        portrayal.zorder = 3
    elif isinstance(agent, DirtCell):
        portrayal.zorder = 0
        if agent.isDirty:
            portrayal.color = "tab:brown"
            portrayal.size = 100
        else:
            portrayal.color = "white"
            portrayal.size = 0
    elif isinstance(agent, ChargingStation):
        portrayal.color = "tab:green"  # cargadores verdes
        portrayal.zorder = 2
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "black"
        portrayal.zorder = 1
    elif isinstance(agent, Wall):
        portrayal.color = "black"
        portrayal.zorder = 0

    return portrayal


# parámetros del modelo que se pueden ajustar en la interfaz
modelParams = {
    "seed": {
        "type": "InputText",
        "value": 50,
        "label": "Random Seed",
    },
    "numAgents": Slider("Number of Roombas", 2, 1, 10),
    "width": Slider("Grid Width", 20, 10, 40),
    "height": Slider("Grid Height", 20, 10, 40),
    "dirtyPercentage": Slider("Dirty Cells (%)", 30, 0, 100),
    "obstaclePercentage": Slider("Obstacles (%)", 10, 0, 100),
    "maxSteps": Slider("Max Steps", 10000, 1000, 100000),
}


def postProcessSpace(ax):
    """ajusta el aspecto del espacio visual."""
    ax.set_aspect("equal")


def postProcessLines(ax):
    """ajusta el aspecto de los gráficos de líneas."""
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))


# componente que visualiza el grid con los agentes
spaceComponent = make_space_component(
    roombaPortrayal,
    draw_grid=False,
    post_process=postProcessSpace,
)

# componente que visualiza gráficos de líneas con datos del modelo
# mismo formato que Sim1: 4 datos
plotComponent = make_plot_component(
    {
        "Movement Count": "tab:blue",
        "Step Limit": "tab:red",
        "Percentage Clean": "tab:green",
        "Battery": "tab:orange"
    },
    post_process=postProcessLines,
)


def metricsComponent(model):
    """
    muestra las estadísticas de la simulación incluyendo métricas por agente.
    parámetros:
        model: modelo de la simulación
    retorna: componente markdown con las métricas
    """
    # obtiene todos los agentes roombas
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    
    # calcula tiles sucias restantes
    totalDirty = sum(1 for a in model.agents if isinstance(a, DirtCell) and a.isDirty)
    
    # obtiene las métricas generales
    metrics = model.getMetrics()

    # construye las métricas individuales de cada agente
    agentMetrics = ""
    for agent in sorted(agents, key=lambda a: a.agentId):
        agentMetrics += f"\n**Roomba {agent.agentId}:** Limpiadas: {agent.cleanedCells} - Movimientos: {agent.movementCount} - Batería: {agent.battery}%\n"

    # retorna un texto formateado con las estadísticas
    return solara.Markdown(f"""
### Estadísticas Generales

- Tiempo total: {model.steps} pasos
-   Tiempo hasta limpiar todo:  {metrics['timeAllClean']} pasos
- Porcentaje de limpieza :   {metrics['percentageClean']:.2f} %
-   Número de Movimientos :{metrics['totalMovements']}
- Batería  promedio:  {metrics['averageBattery']:.2f} %

### Métricas por Agente
{agentMetrics}
""")



# crea la instancia del modelo
model = RandomModel()

# crea la página de visualización con todos los componentes
page = SolaraViz(
    model,
    components=[spaceComponent, plotComponent, metricsComponent],
    model_params=modelParams,
    name="Multi-Roomba Simulation - A01029829",
)