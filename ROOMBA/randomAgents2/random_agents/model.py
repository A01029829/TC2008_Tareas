# simulación 2: modelo de múltiples roombas que se comunican y limpian tiles sucias
# autor: Luis Emilio Veledíaz Flores - A01029829
# fecha: 19 de Noviembre de 2025

from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector

from .agent import RandomAgent, ObstacleAgent, DirtCell, ChargingStation, Wall


class RandomModel(Model):
    """modelo con múltiples agentes roombas que se comunican y limpian tiles sucias."""

    def __init__(self, numAgents=2, width=20, height=20, dirtyPercentage=30, 
                 obstaclePercentage=10, maxSteps=10000, seed=42):
        """
        crea el modelo.
        parámetros:
            numAgents: número de agentes en la simulación
            width: ancho del grid
            height: alto del grid
            dirtyPercentage: porcentaje de tiles sucias (0-100)
            obstaclePercentage: porcentaje de tiles con obstáculos (0-100)
            maxSteps: número máximo de pasos permitidos
            seed: semilla para reproducibilidad
        """
        super().__init__(seed=seed)
        
        # guarda parámetros del modelo
        self.numAgents = numAgents
        self.seed = seed
        self.width = width
        self.height = height
        self.dirtyPercentage = dirtyPercentage
        self.obstaclePercentage = obstaclePercentage
        self.maxSteps = maxSteps
        self.steps = 0
        self.timeAllClean = None
        self.chargingStations = {}

        # crea el grid usando topología Moore (8 vecinos)
        self.grid = OrthogonalMooreGrid([width, height], torus=False, random=self.random)
        self.space = self.grid

        # identifica coordenadas del borde de la grilla
        border = [(x, y)
                  for y in range(height)
                  for x in range(width)
                  if y in [0, height-1] or x in [0, width - 1]]

        # crea paredes invisibles en el borde
        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                Wall(self, cell=cell)

        # obtiene tiles disponibles (sin borde)
        availableCells = [cell for cell in self.grid 
                         if cell.coordinate not in border]

        # calcula número de obstáculos basado en porcentaje
        numObstacles = max(0, int(len(availableCells) * (obstaclePercentage / 100)))

        # crea obstáculos visibles aleatorios
        if numObstacles > 0:
            obstacleCells = self.random.sample(availableCells, numObstacles)
            for cell in obstacleCells:
                ObstacleAgent(self, cell=cell)
                availableCells.remove(cell)

        # crea cargadores en posiciones aleatorias
        numStations = min(numAgents, len(availableCells))
        chargingStationCells = self.random.sample(availableCells, numStations)

        # inicializa los cargadores
        for idx, cell in enumerate(chargingStationCells):
            station = ChargingStation(self, cell=cell, stationId=idx)
            self.chargingStations[cell.coordinate] = station
            availableCells.remove(cell)

        # crea agentes roombas en sus respectivos cargadores
        for idx, cell in enumerate(chargingStationCells):
            if idx < numAgents:
                RandomAgent(self, cell=cell, agentId=idx, homeStationCoord=cell.coordinate)

        # calcula número de tiles sucias basado en porcentaje
        numDirtCells = max(0, int(len(availableCells) * (dirtyPercentage / 100)))

        # crea tiles sucias en ubicaciones aleatorias
        if numDirtCells > 0:
            dirtCells = self.random.sample(availableCells, numDirtCells)
            for cell in dirtCells:
                DirtCell(self, cell=cell)
                availableCells.remove(cell)

        # guarda el número total de tiles sucias
        self.numDirtCells = numDirtCells
        self.running = True

        # configura recopilación de datos del modelo
        self.datacollector = DataCollector(
            model_reporters={
                # número total de movimientos de todos los roombas
                "Movement Count": lambda m: sum(a.movementCount for a in m.agents if isinstance(a, RandomAgent)),
                # tiles limpias en total
                "Percentage Clean": lambda m: (sum(a.cleanedCells for a in m.agents if isinstance(a, RandomAgent)) / m.numDirtCells * 100) if m.numDirtCells > 0 else 0,
                # línea de referencia del límite de pasos
                "Step Limit": lambda m: (m.steps / m.maxSteps * 100) if m.maxSteps > 0 else 0,
                # batería promedio de todos los roombas
                "Battery": lambda m: (sum(a.battery for a in m.agents if isinstance(a, RandomAgent)) / len([a for a in m.agents if isinstance(a, RandomAgent)])) if len([a for a in m.agents if isinstance(a, RandomAgent)]) > 0 else 0,
            },
            agent_reporters={
                "Battery": "battery",
                "Cleaned Cells": "cleanedCells",
                "Movement Count": "movementCount",
                "State": "state",
                "Agent ID": "agentId",
            }
        )
        self.datacollector.collect(self)

    def getMetrics(self):
        """
        obtiene las métricas finales de la simulación.
        retorna: diccionario con métricas globales
        """
        agents = [a for a in self.agents if isinstance(a, RandomAgent)]
        if not agents:
            return None

        totalCleaned = sum(a.cleanedCells for a in agents)
        percentageClean = (totalCleaned / self.numDirtCells * 100) if self.numDirtCells > 0 else 0
        totalMovements = sum(a.movementCount for a in agents)
        avgBattery = sum(a.battery for a in agents) / len(agents) if agents else 0

        return {
            "timeSteps": self.steps,
            "timeAllClean": self.timeAllClean if self.timeAllClean is not None else self.steps,
            "percentageClean": percentageClean,
            "totalMovements": totalMovements,
            "averageBattery": avgBattery,
        }

    def step(self):
        """avanza el modelo un paso."""
        # verifica si se alcanzó el límite de pasos
        if self.steps >= self.maxSteps:
            self.running = False
            return

        # obtiene todos los agentes roomba
        agents = [a for a in self.agents if isinstance(a, RandomAgent)]

        # verifica si todos los roombas se quedaron sin batería
        if all(a.battery <= 0 for a in agents):
            self.running = False
            return

        # ejecuta un paso para todos los agentes
        self.agents.shuffle_do("step")
        self.steps += 1

        # verifica si todas las tiles están limpias
        if self.timeAllClean is None:
            remainingDirty = sum(1 for a in self.agents if isinstance(a, DirtCell) and a.isDirty)
            if remainingDirty == 0:
                self.timeAllClean = self.steps
                self.running = False

        # recopila datos de este paso
        self.datacollector.collect(self)