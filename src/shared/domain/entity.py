from abc import ABC
from typing import Any


class Entity(ABC):
    """
    This is the abstract class for all the entities for the domain.
    With this class we know that all the instances of all the entities
    will be equal if its id is equal and not for its attributes.
    """

    id: Any

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
