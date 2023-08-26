"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from random import random
from exercises.ex09 import constants
from math import sin, cos, pi, sqrt


__author__ = "730569880"


class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)

    def distance(self, other: Point) -> float:
        """Distance formula used to determine if the cells touch."""
        return (sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2)))


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int = constants.VULNERABLE

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction

    def tick(self) -> None:
        """Makes the new location and moves the cell there."""
        self.location = self.location.add(self.direction)
        if self.is_infected():
            self.sickness += 1
        if self.sickness >= constants.RECOVERY_PERIOD:
            self.immunize()

    def contract_disease(self) -> int:
        """Assigns a cell to be get infected."""
        self.sickness = 1

    def is_vulnerable(self) -> bool:
        """Determines if a cell has yet to contract disease or not."""
        if self.sickness == 0:
            return True
        else:
            return False

    def is_infected(self) -> bool:
        """Determines is a cell is infected or not."""
        if self.sickness >= 1:
            return True
        else:
            return False

    def contact_with(self, another: Cell) -> None:
        """Determines which cells come in contact and which contract the disease."""
        if self.is_vulnerable() and another.is_infected():
            self.contract_disease()
        if self.is_infected() and another.is_vulnerable():
            another.contract_disease()

    def immunize(self) -> int:
        """Assigns a cell to be get infected."""
        self.sickness = -1

    def is_immune(self) -> bool:
        """Determines if a cell has yet to contract disease or not."""
        if self.sickness == -1:
            return True
        else:
            return False
    
    def color(self) -> str:
        """Return the color representation of a cell."""
        if self.is_vulnerable():
            return "gray"
        if self.is_infected():
            return "blue"
        if self.is_immune():
            return "green"


class Model:
    """The state of the simulation."""

    population: list[Cell]
    time: int = 0

    def __init__(self, cells: int, speed: float, num_of_inf: int, num_of_im: int = 0):
        """Initialize the cells with random locations and directions."""
        self.population = []

        if num_of_inf <= 0 or num_of_inf >= cells:
            raise ValueError("The number of infected cells must be less than the number of cells but more than 0.")
        if num_of_im < 0 or num_of_im >= cells:
            raise ValueError("The number of immune cells must be less than the number of cells but more than 0.")
        if num_of_im + num_of_inf >= cells:
            raise ValueError("Need some vulnerable cells.")

        for _ in range(cells - num_of_inf - num_of_im):
            start_location: Point = self.random_location()
            start_direction: Point = self.random_direction(speed)
            cell: Cell = Cell(start_location, start_direction)
            self.population.append(cell)
        for _ in range(num_of_inf):
            start_location: Point = self.random_location()
            start_direction: Point = self.random_direction(speed)
            cell: Cell = Cell(start_location, start_direction)
            cell.contract_disease()
            self.population.append(cell)
            
        for _ in range(num_of_im):
            start_location: Point = self.random_location()
            start_direction: Point = self.random_direction(speed)
            cell: Cell = Cell(start_location, start_direction)
            cell.immunize()
            self.population.append(cell)

    def check_contacts(self) -> None:
        """Loop to check to see if and when one cell touches the others."""
        i: int = 0
        while i < len(self.population):
            start: int = i + 1
            for other_cells in range(start, len(self.population)):
                cell: Cell = self.population[i]
                other_cell: Cell = self.population[other_cells]
                if cell.location.distance(other_cell.location) < constants.CELL_RADIUS:
                    cell.contact_with(other_cell)
            i += 1

    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)

        self.check_contacts()
        self.is_complete()
        
    def random_location(self) -> Point:
        """Generate a random location."""
        start_x: float = random() * constants.BOUNDS_WIDTH - constants.MAX_X
        start_y: float = random() * constants.BOUNDS_HEIGHT - constants.MAX_Y
        return Point(start_x, start_y)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle: float = 2.0 * pi * random()
        direction_x: float = cos(random_angle) * speed
        direction_y: float = sin(random_angle) * speed
        return Point(direction_x, direction_y)

    def enforce_bounds(self, cell: Cell) -> None:
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > constants.MAX_X:
            cell.location.x = constants.MAX_X
            cell.direction.x *= -1.0
        if cell.location.x < constants.MIN_X:
            cell.location.x = constants.MIN_X
            cell.direction.x *= -1.0
        if cell.location.y > constants.MAX_Y:
            cell.location.y = constants.MAX_Y
            cell.direction.y *= -1.0
        if cell.location.y < constants.MIN_Y:
            cell.location.y = constants.MIN_Y
            cell.direction.y *= -1.0

    def is_complete(self) -> bool:
        """Method to indicate when the simulation is complete."""
        for cell in self.population:
            if (cell.is_infected()):
                return False
        return True