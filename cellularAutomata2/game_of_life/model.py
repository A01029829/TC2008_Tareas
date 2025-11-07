from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import Cell

class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in Conway's Game of Life."""

    def __init__(self, width=50, height=50, initial_fraction_alive=0.2, seed=None):
        """Create a new playing area of (width, height) cells."""
        super().__init__(seed=seed)

        """Grid where cells are connected to their 8 neighbors.

        Example for two dimensions:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]
        """

        self.grid = OrthogonalMooreGrid((width, height), capacity=1, torus=True)

        # mantener referencias a los agentes por posición para acceso directo
        self.cell_grid = {}

        # colocar una celula en cada sección, y asignar aleatoriamente ALIVE y DEAD
        for cell in self.grid.all_cells:
            x, y = cell.coordinate
            init_state = (
                Cell.ALIVE
                if self.random.random() < initial_fraction_alive
                else Cell.DEAD
            )

            agent = Cell(self, cell, init_state=init_state)
            self.cell_grid[(x, y)] = agent
            
        self.running = True

    def step(self):
        """Perform the model step in two stages:

        - First, all cells compute their next state based on the 3 neighbors above
        - Then, all cells change state to their next state.
        """
        self.agents.do("determine_state")
        self.agents.do("assume_state")