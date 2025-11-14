from mesa.discrete_space import CellAgent, FixedAgent

class RandomAgent(CellAgent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
    """
    def __init__(self, model, cell):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: Reference to its position within the grid
        """
        super().__init__(model)
        self.cell = cell
        self.battery = 100
        self.moves_count = 0
        self.charging_station = (1,1)

    def is_at_charging_station(self):
        """
        Checks if the agent is at the charging station.
        Returns:
            bool: True is agent is at (1, 1)
        """
        return self.cell.coordinate == self.charging_station
    
    def charge_battery(self):
        """
        Charges the battery 5%
        """
        if self.battery < 100:
            self.battery = min(100, self.battery + 5)
    
    def consume_battery(self, amount=1):
        """
        Consumes battery energy for an action. 
        Argument: amount -> percentage of battery to consume
        Returns: bool -> true if it was consumed, false if it has no battery
        """
        if self.battery >= amount:
            self.battery -= amount
            return True
        return False
    
    def clean_cell(self):
        """
        Cleans the current cell (if it's dirty)
        Consumes 1% battery
        Returns: bool -> true if cell was cleaned, false otherwise
        """
        if self.cell.is_dirty and self.consume_battery(1):
            self.cell.is_dirty = False
            return True
        return False

    def move(self):
        """
        Determines the next empty cell in its neighborhood, and moves to it
        """
        if not self.consume_battery(1):
            return False
        
        next_moves = self.cell.neighborhood.select(lambda cell: cell.is_empty)

        if len(next_moves.cells) > 0:
            self.cell = next_moves.select_random_cell()
            self.moves_count += 1
            return True
        
        return False

    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        if self.battery <= 0:
            return  # Agent cannot act without battery
        
        # If at charging station
        if self.is_at_charging_station():
            if self.battery < 100:
                self.charge_battery()
                return  # Charging takes the step
            else:
                # Battery is full, leave the station
                self.move()
                return
        
        # NOT at charging station
        # Priority 1: Clean if current cell is dirty
        if self.cell.is_dirty:
            self.clean_cell()
            return
        
        # Priority 2: If battery is low, go back to charging station
        if self.battery < 20:
            # Move toward charging station (simple approach: move toward it)
            self.move_toward_target(self.charging_station)
            return
        
        # Priority 3: Move randomly to explore and clean other cells
        self.move()

    def move_toward_target(self, target_coordinate):
        """
        Attempts to move closer to a target coordinate.
        Uses Manhattan distance to determine best direction.
        Consumes 1% battery if successful.
        
        Args:
            target_coordinate: Tuple (x, y) of target location
        """
        if not self.consume_battery(1):
            return False
        
        current_x, current_y = self.cell.coordinate
        target_x, target_y = target_coordinate
        
        # Get valid neighboring cells
        neighbors = self.cell.neighborhood.select(lambda cell: cell.is_empty)
        
        if len(neighbors.cells) == 0:
            return False
        
        # Find the neighbor closest to target using Manhattan distance
        best_cell = None
        best_distance = float('inf')
        
        for neighbor_cell in neighbors.cells:
            neighbor_x, neighbor_y = neighbor_cell.coordinate
            # Calculate Manhattan distance from this neighbor to target
            distance = abs(neighbor_x - target_x) + abs(neighbor_y - target_y)
            
            if distance < best_distance:
                best_distance = distance
                best_cell = neighbor_cell
        
        if best_cell:
            self.cell = best_cell
            self.moves_count += 1
            return True
        
        return False

class ObstacleAgent(FixedAgent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell

    def step(self):
        pass

class DirtCell:
    """
    is_dirty: Cell is dirty = true
    is_empty: Cell has no agents
    """
    def __init__(self, original_cell):
        self.original_cell = original_cell
        self.is_dirty = True  
        self.is_empty = original_cell.is_empty
        self.coordinate = original_cell.coordinate
        self.neighborhood = original_cell.neighborhood

    def __getattr__(self, name):
        """Delegate other attributes to the original cell"""
        return getattr(self.original_cell, name)