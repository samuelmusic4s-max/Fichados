from abc import ABC


class ValueObject(ABC):
    """
    This is the abstract class for every value object
    that we will use in this project.
    It is for defininng the eq rules that will be true
    only if all the attributes are equal too.
    """

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self) -> int:
        return hash(tuple(self.__dict__.items()))
