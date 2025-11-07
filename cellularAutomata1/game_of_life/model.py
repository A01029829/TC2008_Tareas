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
        # referencia a los agentes por posición
        self.cell_grid = {}

        # la fila que ya fue actualizada (height - 1 = fila superior)
        self.current_row = height - 1

        # inicializar todas las celdas
        for cell in self.grid.all_cells:
            x, y = cell.coordinate
            if y == 49:
                initial_state = (
                    Cell.ALIVE
                    if self.random.random() < initial_fraction_alive
                    else Cell.DEAD
                )
            else:
                initial_state = Cell.DEAD

            agent = Cell(self, cell, init_state=initial_state)
            self.cell_grid[(x, y)] = agent

        self.running = True

    def step(self):
        """Goes one row down for each step. Each step updates the next row based on the
        top three cells and according to the rules of the exercise.
        
        Stops when the row is zero.
        """
        width = self.grid.width

        # si ya actualizamos hasta la última fila (fila 0), detenemos
        if self.current_row <= 0:
            self.running = False
            return

        # define la fila actual y la que sigue
        prev_row = self.current_row
        next_row = prev_row - 1

        # para cada columna calculamos el estado de la celda en la fila siguiente
        for x in range(width):
            # los 3 vecinos en la fila superior
            left_pos = ((x - 1) % width, prev_row)
            center_pos = (x, prev_row)
            right_pos = ((x + 1) % width, prev_row)

            # obtener los agentes en esas posicionesntes
            left_agent = self.cell_grid[left_pos]
            center_agent = self.cell_grid[center_pos]
            right_agent = self.cell_grid[right_pos]

            # obtener la celda que vamos a actualizar
            next_pos = (x, next_row)
            next_agent = self.cell_grid[next_pos]

            # calcular siguiente estado (set_next_state de agent.py)
            next_agent.set_next_state(
                left_agent.state,
                center_agent.state,
                right_agent.state,
            )

        # aplicar los next_state para toda la fila
        for x in range(width):
            next_agent = self.cell_grid[(x, next_row)]
            next_agent.assume_state()

        # marcar que la fila ya fue actualizada para ir a la de abajo
        self.current_row = next_row