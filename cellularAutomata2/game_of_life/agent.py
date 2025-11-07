from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    RULE_SET = {
        "000": 0,  # Dead
        "001": 1,  # Alive
        "010": 0,  # Dead
        "011": 1,  # Alive
        "100": 1,  # Alive
        "101": 0,  # Dead
        "110": 1,  # Alive
        "111": 0,  # Dead
    }

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model) # super llama al constructor de la clase padre
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """

        # obtener coordenadas y dimensiones
        x, y = self.x, self.y
        width = self.model.grid.width
        height = self.model.grid.height

        # calcular la fila de arriba
        upper_y = (y+1) % height

        # posiciones de los 3 vecinos superiores
        left_pos = ((x - 1) % width, upper_y)
        center_pos = (x, upper_y)
        right_pos = ((x + 1) % width, upper_y)

        # obtener los agentes en esas posiciones
        left_agent = self.model.cell_grid.get(left_pos)
        center_agent = self.model.cell_grid.get(center_pos)
        right_agent = self.model.cell_grid.get(right_pos)

        # extraer los estados de esos agentes
        left_state = left_agent.state
        center_state = center_agent.state
        right_state = right_agent.state

        # casos para determinar si está vivo o muerto
        a = 1 if left_state == self.ALIVE else 0
        b = 1 if center_state == self.ALIVE else 0
        c = 1 if right_state == self.ALIVE else 0

         # crear patrón como un string
        pattern = f"{a}{b}{c}"

        # aplicar la regla consultando el diccionario
        self._next_state = self.RULE_SET[pattern]

    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state #asignar el siguiente estado
