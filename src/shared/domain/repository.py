from abc import ABC, abstractmethod
from .entity import Entity
from typing import TypeVar, Generic, List


T = TypeVar("T", bound=Entity)


class Repository(ABC, Generic[T]):
    """
    This is the father of all repositories
    """

    @abstractmethod
    def save(self, entity: T) -> None:
        """
        This method saves an entity to the
        repository of that entity.
        """
        pass

    @abstractmethod
    def findById(self, id: str) -> T | None:
        """
        This method search the entity by its id
        and returns it if it is found, else it returns
        null
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        """
        This method updates an entity of the repository
        with the new information of the object
        """
        pass
