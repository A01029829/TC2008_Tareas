# simulación 2: múltiples roombas que se comunican y limpian tiles sucias
# autor: Luis Emilio Veledíaz Flores - A01029829
# fecha: 19 de Noviembre de 2025

from mesa.discrete_space import CellAgent, FixedAgent


class DirtCell(FixedAgent):
    """tile sucia que puede ser limpiada por los agentes."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        self.isDirty = True

    def step(self):
        pass

    def clean(self):
        """marca la tile como limpia."""
        self.isDirty = False


class ChargingStation(FixedAgent):
    """cargador donde los agentes recargan batería."""

    def __init__(self, model, cell, stationId):
        super().__init__(model)
        self.cell = cell
        self.stationId = stationId
        self.occupiedBy = None  # agente que la está usando
        self.isOccupied = False

    def step(self):
        pass

    def occupy(self, agent):
        """marca el cargador como ocupado por un agente."""
        self.occupiedBy = agent
        self.isOccupied = True

    def release(self):
        """libera el cargador."""
        self.occupiedBy = None
        self.isOccupied = False


class RandomAgent(CellAgent):
    """agente que limpia tiles sucias, gestiona batería y se comunica con otros roombas."""

    def __init__(self, model, cell, agentId, homeStationCoord):
        """
        crea un nuevo agente roomba.
        parámetros:
            model: referencia al modelo
            cell: posición inicial del agente en el grid
            agentId: identificador único del agente
            homeStationCoord: coordenadas de su cargador inicial
        """
        super().__init__(model)
        self.cell = cell
        self.agentId = agentId
        self.battery = 100
        self.cleanedCells = 0
        self.movementCount = 0
        self.chargingTurns = 0
        self.state = "exploring"
        self.visited = {cell.coordinate}
        self.homeStation = homeStationCoord
        self.knownChargingStations = {homeStationCoord}
        self.currentStation = None  # cargador que está ocupando

    def _isSafe(self, cell):
        """verifica si una tile es segura para moverse sin obstáculos."""
        for agent in cell.agents:
            if isinstance(agent, (ObstacleAgent, Wall)):
                return False
        return True

    def _distanceToStation(self, stationCoord, cell=None):
        """calcula la distancia manhattan a un cargador."""
        if cell is None:
            cell = self.cell
        
        x, y = cell.coordinate
        stationX, stationY = stationCoord
        return abs(x - stationX) + abs(y - stationY)

    def _NearbyRoombas(self):
        """chatea con roombas en la vecindad Moore para intercambiar cargadores conocidos."""
        # obtiene todos los vecinos (vecindad Moore = 8 tiles circundantes)
        neighbors = list(self.cell.neighborhood) + [self.cell]
        
        # busca roombas en cualquiera de las tiles vecinas
        for neighbor_cell in neighbors:
            for agent in neighbor_cell.agents:
                if isinstance(agent, RandomAgent) and agent.agentId != self.agentId:
                    # intercambia conocimiento de cargadores con el otro roomba
                    self.knownChargingStations.update(agent.knownChargingStations)
                    agent.knownChargingStations.update(self.knownChargingStations)

    def _nearestKnownStation(self):
        """retorna el cargador más cercana que conoce."""
        if not self.knownChargingStations:
            return self.homeStation
        
        nearest = None
        minDist = float('inf')
        
        for stationCoord in self.knownChargingStations:
            dist = self._distanceToStation(stationCoord)
            if dist < minDist:
                minDist = dist
                nearest = stationCoord
        
        return nearest

    def _needToCharge(self):
        """verifica si necesita recargar según batería y distancia al cargador más cercano."""
        nearestStation = self._nearestKnownStation()
        distance = self._distanceToStation(nearestStation)
        return self.battery <= 30 or self.battery <= distance + 5

    def _getSafeNeighbors(self):
        """retorna lista de vecinos sin obstáculos."""
        return [n for n in self.cell.neighborhood if self._isSafe(n)]

    def _hasDirtInCell(self):
        """verifica si hay suciedad en la tile actual."""
        for agent in self.cell.agents:
            if isinstance(agent, DirtCell) and agent.isDirty:
                return True
        return False

    def _findDirtyNeighbor(self):
        """busca entre los 8 vecinos si hay alguno con suciedad."""
        safeNeighbors = self._getSafeNeighbors()
        
        for neighbor in safeNeighbors:
            for agent in neighbor.agents:
                if isinstance(agent, DirtCell) and agent.isDirty:
                    return neighbor
        
        return None

    def _isInCharger(self):
        """verifica si el agente está en un cargador."""
        for agent in self.cell.agents:
            if isinstance(agent, ChargingStation):
                self.knownChargingStations.add(self.cell.coordinate)
                return True
        return False

    def _canOccupyStation(self):
        """verifica si puede ocupar un cargador."""
        for agent in self.cell.agents:
            if isinstance(agent, ChargingStation):
                # si no está ocupada, o si está ocupada por este agente, puede ocuparla
                if not agent.isOccupied or agent.occupiedBy == self:
                    return agent
        return None

    def _releaseStation(self):
        """libera el cargador que ocupa actualmente."""
        if self.currentStation:
            self.currentStation.release()
            self.currentStation = None

    def moveTowardsNearestStation(self):
        """se mueve hacia el cargador más cercano usando distancia manhattan."""
        nearestStation = self._nearestKnownStation()
        safeNeighbors = self._getSafeNeighbors()
        
        if not safeNeighbors:
            return
        
        bestCell = None
        bestDistance = None
        
        for neighbor in safeNeighbors:
            distance = self._distanceToStation(nearestStation, neighbor)
            
            if bestDistance is None or distance < bestDistance:
                bestDistance = distance
                bestCell = neighbor
        
        if bestCell is not None:
            self.moveToCell(bestCell)

    def moveToUnvisited(self):
        """se mueve a un vecino no visitado o aleatoriamente entre vecinos seguros."""
        safeNeighbors = self._getSafeNeighbors()
        if not safeNeighbors:
            return

        unvisitedNeighbors = [n for n in safeNeighbors if n.coordinate not in self.visited]

        if unvisitedNeighbors:
            target = self.random.choice(unvisitedNeighbors)
        else:
            target = self.random.choice(safeNeighbors)

        self.moveToCell(target)

    def moveToCell(self, cell):
        """
        mueve el agente a una tile específica y actualiza métricas.
        parámetros:
            cell: tile destino
        """
        if cell is None:
            return

        self.cell = cell
        self.battery = max(0, self.battery - 1)
        self.movementCount += 1

        if hasattr(self.cell, "coordinate"):
            self.visited.add(self.cell.coordinate)

    def clean(self):
        """limpia la tile actual si contiene suciedad."""
        for agent in self.cell.agents:
            if isinstance(agent, DirtCell) and agent.isDirty:
                agent.clean()
                self.battery = max(0, self.battery - 1)
                self.cleanedCells += 1
                return True
        
        return False

    def charge(self):
        """carga la batería si está en un cargador y puede ocuparlo."""
        station = self._canOccupyStation()
        
        if station:
            # ocupa el cargador si no estaba ocupado
            if not station.isOccupied:
                station.occupy(self)
                self.currentStation = station
            
            # solo carga si la ocupa este agente
            if station.occupiedBy == self:
                if self.battery < 100:
                    self.battery = min(100, self.battery + 5)
                    self.chargingTurns += 1
                    return True
        
        return False

    def explore(self):
        """explora moviéndose a una tile no visitada."""
        self.moveToUnvisited()

    def step(self):
        """ejecuta un paso del agente con máquina de estados."""
        if self.battery <= 0:
            self.state = "charging"
            # libera el cargador si lo ocupa
            self._releaseStation()
            return

        # chatea con roombas en la vecindad Moore
        self._NearbyRoombas()

        if self.state == "charging":
            if self._isInCharger():
                self.charge()
                if self.battery >= 80:
                    self.state = "exploring"
                    # libera el cargador cuando sale
                    self._releaseStation()
            else:
                self.state = "moving_to_charge"

        elif self.state == "moving_to_charge":
            self.moveTowardsNearestStation()
            if self._isInCharger():
                self.state = "charging"

        elif self.state == "exploring":
            if self._hasDirtInCell():
                self.state = "cleaning"
            elif self._findDirtyNeighbor() is not None:
                self.state = "moving_to_dirt"
            elif self._needToCharge():
                self.state = "moving_to_charge"
            else:
                self.explore()

        elif self.state == "cleaning":
            cleaned = self.clean()

            if not cleaned:
                self.state = "exploring"
            elif self._needToCharge():
                self.state = "moving_to_charge"

        elif self.state == "moving_to_dirt":
            dirtyNeighbor = self._findDirtyNeighbor()
            if dirtyNeighbor is not None:
                self.moveToCell(dirtyNeighbor)
            else:
                self.state = "exploring"

            if self._hasDirtInCell():
                self.state = "cleaning"
            elif self._needToCharge():
                self.state = "moving_to_charge"


class Wall(FixedAgent):
    """paredes invisibles en el borde de la grilla."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class ObstacleAgent(FixedAgent):
    """obstáculos visibles dentro de la grilla."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass