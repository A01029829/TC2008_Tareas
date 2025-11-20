# simulación 1: roomba individual que limpia tiles sucias
# autor: Luis Emilio Veledíaz Flores - A01029829
# fecha: 19 de Noviembre de 2025

from mesa.discrete_space import CellAgent, FixedAgent


class DirtCell(FixedAgent):
    """tile sucia que puede ser limpiada por el agente."""

    def __init__(self, model, cell):
        # inicializa la tile sucia
        super().__init__(model)
        self.cell = cell
        self.isDirty = True  # marca la tile como sucia

    def step(self):
        # las tiles sucias no realizan acciones
        pass

    def clean(self):
        """marca la tile como limpia."""
        self.isDirty = False  # cambia el estado de sucia a limpia


class ChargingStation(FixedAgent):
    """cargador donde el agente recarga batería."""

    def __init__(self, model, cell):
        # inicializa el cargador
        super().__init__(model)
        self.cell = cell

    def step(self):
        # el cargador no tiene acciones
        pass


class RandomAgent(CellAgent):
    """agente que limpia tiles sucias y gestiona batería con máquina de estados."""

    def __init__(self, model, cell):
        """
        crea un nuevo agente roomba.
        parámetros:
            model: referencia al modelo
            cell: posición inicial del agente en el grid
        """
        super().__init__(model)
        self.cell = cell
        self.battery = 100  # batería inicial al 100%
        self.cleanedCells = 0  # contador de tiles limpias
        self.state = "exploring"  # el estado inicial es explorar
        self.movementCount = 0  # contador de movimientos realizados
        self.chargingTurns = 0  # contador de veces que se cargó
        self.visited = set()  # conjunto de tiles visitadas
        self.chargingStationPos = cell.coordinate  # posición del cargador
        self.visitCount = {}  # contador de visitas por tile para priorizar no visitadas

        # marca posición inicial como visitada
        if hasattr(self.cell, "coordinate"):
            self.visited.add(self.cell.coordinate)
            self.visitCount[self.cell.coordinate] = 1

    def _isSafe(self, cell):
        """verifica si una tile es segura para moverse sin obstáculos."""
        # revisa si la tile tiene obstáculos o paredes
        for agent in cell.agents:
            if isinstance(agent, (ObstacleAgent, Wall)):
                return False  # tile no segura si tiene obstáculo
        return True  # tile segura si no tiene obstáculos

    def _distanceToCharger(self, cell=None):
        """calcula la distancia manhattan hasta el cargador."""
        if cell is None:
            cell = self.cell  # si no especifica tile, usa la actual
        
        # obtiene las coordenadas de la tile actual
        x, y = cell.coordinate
        chargerX, chargerY = self.chargingStationPos  # coordenadas del cargador
        
        # distancia manhattan: suma de diferencias en x e y
        return abs(x - chargerX) + abs(y - chargerY)

    def _needToCharge(self):
        """verifica si necesita recargar según batería y distancia al cargador."""
        distance = self._distanceToCharger()
        
        # necesita cargar si batería <= 30 o si no tiene suficiente para volver
        return self.battery <= 30 or self.battery <= distance + 5

    def _getSafeNeighbors(self):
        """retorna lista de vecinos sin obstáculos."""
        safeNeighbors = []
        
        # revisa cada vecino (8 direcciones)
        for neighbor in self.cell.neighborhood:
            if self._isSafe(neighbor):  # solo agrega si es segura
                safeNeighbors.append(neighbor)
        
        return safeNeighbors

    def _hasDirtInCell(self):
        """verifica si hay suciedad en la tile actual."""
        # busca entre los agentes de la tile actual
        for agent in self.cell.agents:
            if isinstance(agent, DirtCell) and agent.isDirty:
                return True  # encontró suciedad
        return False  # no hay suciedad

    def _findDirtyNeighbor(self):
        """busca entre los 8 vecinos si hay alguno con suciedad."""
        safeNeighbors = self._getSafeNeighbors()
        
        # revisa cada vecino seguro
        for neighbor in safeNeighbors:
            # busca si tiene suciedad
            for agent in neighbor.agents:
                if isinstance(agent, DirtCell) and agent.isDirty:
                    return neighbor  # retorna el vecino con suciedad
        
        return None  # no encontró suciedad en vecinos

    def _isInCharger(self):
        """verifica si el agente está en el cargador."""
        # busca entre los agentes de la tile actual
        for agent in self.cell.agents:
            if isinstance(agent, ChargingStation):
                return True  # está en el cargador
        return False  # no está en el cargador

    def moveTowardsCharger(self):
        """se mueve hacia el cargador usando distancia manhattan."""
        safeNeighbors = self._getSafeNeighbors()
        if not safeNeighbors:
            return  # no hay vecinos seguros, no puede moverse

        # encontrar el vecino que reduce la distancia al cargador
        bestCell = None
        bestDistance = None

        # evalua cada vecino seguro
        for neighbor in safeNeighbors:
            distance = self._distanceToCharger(neighbor)  # calcula distancia
            
            # si es la primera vez o es más cercana que la anterior
            if bestDistance is None or distance < bestDistance:
                bestDistance = distance
                bestCell = neighbor

        # se mueve al vecino más cercano al cargador
        if bestCell is not None:
            self.moveToCell(bestCell)

    def _findUnvisited(self):
        """busca la tile no visitada más cercana usando BFS."""
        queue = [(self.cell, [self.cell])]
        visited = {self.cell}
        index = 0
        
        while index < len(queue):
            currentCell, path = queue[index]
            index += 1
            
            # si encontramos una tile no visitada, retorna el camino
            if currentCell.coordinate not in self.visited:
                return path
            
            # expandir búsqueda a vecinos seguros
            for neighbor in currentCell.neighborhood:
                if neighbor not in visited and self._isSafe(neighbor):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # no hay tile no visitadas accesibles

    def moveToUnvisited(self):
        """se mueve a un tile no visitada usando BFS o explora localmente."""
        # buscar tile no visitada más cercana
        path = self._findUnvisited()
        
        if path and len(path) > 1:
            # moverse al siguiente paso del camino hacia la tile no visitada
            self.moveToCell(path[1])
        else:
            # si no hay tile no visitadas, moverse al vecino menos visitado
            safeNeighbors = self._getSafeNeighbors()
            if safeNeighbors:
                leastVisited = min(safeNeighbors, key=lambda n: self.visitCount.get(n.coordinate, 0))
                self.moveToCell(leastVisited)

    def moveToCell(self, cell):
        """
        mueve el agente a una tile específica y actualiza métricas.
        parámetros:
            cell: tile destino
        """
        if cell is None:
            return  # no hace nada si la tile es nula

        self.cell = cell  # actualiza posición
        self.battery = max(0, self.battery - 1)  # consume 1% de batería
        self.movementCount += 1  # incrementa contador de movimientos

        # marca como visitada y actualiza contador
        if hasattr(self.cell, "coordinate"):
            self.visited.add(self.cell.coordinate)
            self.visitCount[self.cell.coordinate] = self.visitCount.get(self.cell.coordinate, 0) + 1

    def clean(self):
        """limpia la tile actual si contiene suciedad."""
        # busca si hay suciedad en la tile actual
        for agent in self.cell.agents:
            if isinstance(agent, DirtCell) and agent.isDirty:
                agent.clean()  # limpia la tile sucia
                self.battery = max(0, self.battery - 1)  # consume 1% de batería
                self.cleanedCells += 1  # incrementa contador
                return True  # limpieza exitosa
        
        return False  # no había suciedad que limpiar

    def charge(self):
        """carga la batería si está en el cargador."""
        if self._isInCharger():  # verifica que esté en el cargador
            if self.battery < 100:  # solo carga si no está llena
                self.battery = min(100, self.battery + 5)  # suma 5% de batería
                self.chargingTurns += 1  # incrementa contador de cargas
                return True  # carga exitosa
        return False  # no cargó

    def explore(self):
        """explora moviéndose a una tile no visitada o poco visitada."""
        self.moveToUnvisited()  # se mueve a una tile no visitada o menos visitada

    def step(self):
        """ejecuta un paso del roomba con máquina de estados."""
        # si no tiene batería, no puede hacer nada
        if self.battery <= 0:
            self.state = "charging"
            return

        # máquina de estados con 5 estados posibles
        if self.state == "charging":
            # estado: cargando batería
            if self._isInCharger():
                self.charge()  # intenta cargar
                if self.battery >= 80:
                    self.state = "exploring"  # sale a explorar cuando llega a 80%
            else:
                # no está en el cargador, debe ir hacia el
                self.state = "moving_to_charge"

        elif self.state == "moving_to_charge":
            # estado: moviéndose hacia el cargador
            self.moveTowardsCharger()  # se mueve hacia el cargador
            if self._isInCharger():
                self.state = "charging"  # cambia a cargando cuando llega

        elif self.state == "exploring":
            # estado: explorando el grid
            # prioridad 1: limpiar si hay suciedad en tile actual
            if self._hasDirtInCell():
                self.state = "cleaning"
            # prioridad 2: buscar suciedad en vecinos
            elif self._findDirtyNeighbor() is not None:
                self.state = "moving_to_dirt"
            # prioridad 3: ir a cargar si batería es baja
            elif self._needToCharge():
                self.state = "moving_to_charge"
            # prioridad 4: explorar tile no visitadas
            else:
                self.explore()

        elif self.state == "cleaning":
            # estado: limpiando la tile actual
            cleaned = self.clean()  # intenta limpiar

            if not cleaned:
                # ya no hay suciedad en esta tile, vuelve a explorar
                self.state = "exploring"
            elif self._needToCharge():
                # si durante la limpieza la batería baja mucho, va a cargar
                self.state = "moving_to_charge"

        elif self.state == "moving_to_dirt":
            # estado: moviéndose hacia una tile sucia cercana
            dirtyNeighbor = self._findDirtyNeighbor()
            if dirtyNeighbor is not None:
                self.moveToCell(dirtyNeighbor)  # se mueve hacia la suciedad
            else:
                # ya no hay suciedad en vecinos, vuelve a explorar
                self.state = "exploring"

            # verifica si llegó a suciedad o si necesita cargar
            if self._hasDirtInCell():
                self.state = "cleaning"
            elif self._needToCharge():
                self.state = "moving_to_charge"


class Wall(FixedAgent):
    """paredes invisibles en el borde de la grilla."""

    def __init__(self, model, cell):
        # inicializa la pared
        super().__init__(model)
        self.cell = cell

    def step(self):
        # las paredes no realizan acciones
        pass


class ObstacleAgent(FixedAgent):
    """obstáculos visibles dentro de la grilla."""

    def __init__(self, model, cell):
        # inicializa el obstáculo
        super().__init__(model)
        self.cell = cell

    def step(self):
        # los obstáculos no realizan acciones
        pass