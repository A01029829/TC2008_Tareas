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
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE
    
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model) # super llama al constructor de la clase padre
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def set_next_state(self, left_state, center_state, right_state):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """
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