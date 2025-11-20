# simulación 1: modelo de roomba individual que limpia tiles sucias
# autor: Luis Emilio Veledíaz Flores - A01029829
# fecha: 19 de Noviembre de 2025

from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector

from .agent import RandomAgent, ObstacleAgent, DirtCell, ChargingStation


class RandomModel(Model):
    """modelo con un roomba que limpia tiles sucias."""

    steps = 0

    def __init__(self, numAgents=1, width=20, height=20, dirtyPercentage=30, obstaclePercentage=15, maxSteps=10000, seed=42):
        """
        crea el modelo.
        parámetros:
            numAgents: número de agentes en la simulación
            width: ancho del grid
            height: alto del grid
            dirtyPercentage: porcentaje de tiles sucias (0-100)
            obstaclePercentage: porcentaje de tiles con obstáculos (0-100)
            maxSteps: número máximo de pasos permitidos
            seed: semilla
        """
        super().__init__(seed=seed)
        
        # guarda parámetros del modelo
        self.numAgents = numAgents
        self.seed = seed
        self.width = width
        self.height = height
        self.dirtyPercentage = dirtyPercentage
        self.obstaclePercentage = obstaclePercentage
        self.maxSteps = maxSteps  # límite máximo de pasos
        self.steps = 0  # contador de pasos de simulación
        self.timeAllClean = None  # tiempo cuando todas las tiles se limpian

        # crea el grid usando topología Moore (8 vecinos)
        self.grid = OrthogonalMooreGrid([width, height], torus=False, random=self.random)
        self.space = self.grid

        # identifica coordenadas del borde de la grid
        border = [(x, y)
                  for y in range(height)
                  for x in range(width)
                  if y in [0, height-1] or x in [0, width - 1]]

        # crea obstáculos invisibles en el borde (paredes para contener el grid)
        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                ObstacleAgent(self, cell=cell)

        # crea cargador en posición [1, 1]
        chargingCell = self.grid[1, 1]
        ChargingStation(self, cell=chargingCell)

        # crea roomba en la cargador
        RandomAgent(self, cell=chargingCell)

        # obtiene tiles disponibles (sin borde ni cargador)
        availableCells = [cell for cell in self.grid
                         if cell.coordinate not in border and cell != chargingCell]

        # calcula número de obstáculos basado en porcentaje
        numObstacles = max(0, int(len(availableCells) * (obstaclePercentage / 100)))

        # crea obstáculos visibles aleatorios en el interior
        if numObstacles > 0:
            obstacleCells = self.random.sample(availableCells, numObstacles)
            for cell in obstacleCells:
                ObstacleAgent(self, cell=cell)
                availableCells.remove(cell)

        # calcula número de tiles sucias basado en porcentaje
        numDirtCells = max(0, int(len(availableCells) * (dirtyPercentage / 100)))

        # crea tiles sucias en ubicaciones aleatorias
        dirtCells = self.random.sample(availableCells, numDirtCells)
        for cell in dirtCells:
            DirtCell(self, cell=cell)
            availableCells.remove(cell)

        # guarda el número total de tiles sucias para calcular porcentaje después
        self.numDirtCells = numDirtCells
        self.running = True  # bool de simulación activa

        # configura recopilación de datos del modelo
        self.datacollector = DataCollector(
            model_reporters={
                # reporta número total de movimientos realizados
                "Movement Count": lambda m: m.agents_by_type[RandomAgent][0].movementCount if len(m.agents_by_type[RandomAgent]) > 0 else 0,
                # reporta porcentaje de limpieza calculado en tiempo real
                "Percentage Clean": lambda m: (m.agents_by_type[RandomAgent][0].cleanedCells / m.numDirtCells * 100) if len(m.agents_by_type[RandomAgent]) > 0 and m.numDirtCells > 0 else 0,
                # reporta el límite de steps (línea de referencia)
                "Step Limit": lambda m: (m.steps / m.maxSteps * 100) if m.maxSteps > 0 else 0,
                # reporta la batería actual del roomba
                "Battery": lambda m: m.agents_by_type[RandomAgent][0].battery if len(m.agents_by_type[RandomAgent]) > 0 else 0,
            }
        )
        self.datacollector.collect(self)  # recopila datos iniciales

    def getMetrics(self):
        """
        obtiene las métricas finales de la simulación.
        retorna: diccionario con métricas o None si no hay agente
        """
        # obtiene el único roomba
        agent = self.agents_by_type[RandomAgent][0] if len(self.agents_by_type[RandomAgent]) > 0 else None
        if not agent:
            return None

        totalDirtCells = self.numDirtCells  # total de tiles sucias al inicio
        cleanedCells = agent.cleanedCells  # tiles que limpió el agente
        # calcula tiles sucias restantes
        remainingDirty = sum(1 for a in self.agents if isinstance(a, DirtCell) and a.isDirty)

        # calcula porcentaje de limpieza respecto al total
        percentageClean = (cleanedCells / totalDirtCells * 100) if totalDirtCells > 0 else 0

        # construye diccionario con métricas importantes
        metrics = {
            "timeSteps": self.steps,  # pasos totales de simulación
            "timeAllClean": self.timeAllClean if self.timeAllClean is not None else self.steps,  # pasos para limpiar todo
            "percentageClean": percentageClean,  # porcentaje de limpieza
            "movementCount": agent.movementCount,  # movimientos realizados
        }

        return metrics

    def step(self):
        """avanza el modelo un paso."""
        # verifica si se alcanzó el límite de pasos
        if self.steps >= self.maxSteps:
            self.running = False
            return

        # obtiene el roomba
        agent = self.agents_by_type[RandomAgent][0] if len(self.agents_by_type[RandomAgent]) > 0 else None
        
        # verifica si el roomba se quedó sin batería
        if agent and agent.battery <= 0:
            self.running = False  # detiene la simulación
            return

        # ejecuta un paso para todos los agentes (en orden aleatorio)
        self.agents.shuffle_do("step")
        self.steps += 1  # incrementa contador de pasos

        # verifica si todas las tiles están limpias
        if self.timeAllClean is None:
            remainingDirty = sum(1 for a in self.agents if isinstance(a, DirtCell) and a.isDirty)
            if remainingDirty == 0:
                self.timeAllClean = self.steps  # registra el tiempo de limpieza completa
                self.running = False  # detiene la simulación

        # recopila datos de este paso
        self.datacollector.collect(self)