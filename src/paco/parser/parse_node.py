from abc import ABC, abstractmethod
import numpy as np
from overrides import overrides


class ParseNode(ABC):
    # types = ['task', 'sequential', 'parallel', 'natural', 'choice', 'loop', 'loop_probability']
    def __init__(self, parent, index_in_parent, id: int) -> None:
        self.id = id
        self.parent = parent
        self.index_in_parent = index_in_parent

    @abstractmethod
    def dot(self):
        pass

    @abstractmethod
    def copy(self) -> 'ParseNode(ABC)':
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        return {"id": self.id, "index_in_parent": self.index_in_parent, "type": self.__class__.__name__.lower()}

    @abstractmethod
    def to_dict_id_node(self) -> dict:
        pass

    def __eq__(self, other: 'ParseNode(ABC)') -> bool:
        if not isinstance(other, (Task, Sequential, Parallel, Nature, Choice, Loop)):
            return False

        return self.id == other.id

    def __lt__(self, other: 'ParseNode(ABC)') -> bool:
        if isinstance(other, Task) or isinstance(other, Sequential) or isinstance(other, Parallel) or isinstance(other,
                                                                                                                 Nature) or isinstance(
            other, Choice):
            return self.id < other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self) -> str:
        return str(self.id)


class Gateway(ParseNode, ABC):
    def __init__(self, parent: 'Gateway', index_in_parent: int, id: int) -> None:
        super().__init__(parent, index_in_parent, id)
        self.children = None

    def to_dict_id_node(self) -> dict:
        tmp = {self.id: self}
        for child in self.children:
            if child:
                tmp.update(child.to_dict_id_node())

        return tmp

    def set_children(self, children) -> None:
        self.children = children

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "children": [child.to_dict() for child in self.children] if self.children else None
        })
        return base


class Sequential(Gateway):
    def __init__(self, parent: Gateway, index_in_parent: int, id: int) -> None:
        super().__init__(parent, index_in_parent, id)

    def dot(self):
        return f'\n node_{self.id}[label="Sequential id: {self.id}"];'

    def copy(self) -> 'Sequential':
        parent_copy = self.parent.copy() if self.parent else None
        root_copy = Sequential(parent_copy, self.index_in_parent, self.id)
        root_copy.set_children([child.copy() for child in self.children] if self.children else [])
        return root_copy


class Parallel(Gateway):
    def __init__(self, parent: Gateway, index_in_parent: int, id: int) -> None:
        super().__init__(parent, index_in_parent, id)

    def dot(self):
        return f'\n node_{self.id}[shape=diamond label="Parallel id:{self.id}"];'

    def copy(self) -> 'Parallel':
        parent_copy = self.parent.copy() if self.parent else None
        root_copy = Parallel(parent_copy, self.index_in_parent, self.id)
        root_copy.set_children([child.copy() for child in self.children] if self.children else [])
        return root_copy


class ExclusiveGateway(Gateway, ABC):
    def __init__(self, parent: Gateway, index_in_parent: int, id: int, name: str) -> None:
        super().__init__(parent, index_in_parent, id)
        self.name = name

    @abstractmethod
    def to_dict(self) -> dict:
        base = {"label": self.name}
        base.update(super().to_dict())
        return base


class Choice(ExclusiveGateway):
    def __init__(self, parent: Gateway, index_in_parent: int, id: int, name: str, max_delay: int) -> None:
        super().__init__(parent, index_in_parent, id, name)
        self.max_delay = max_delay

    def dot(self):
        return f'\n node_{self.id}[shape=diamond label="{self.name} id:{self.id} dly:{self.max_delay}" style="filled" fillcolor=orange];'

    def copy(self) -> 'Choice':
        parent_copy = self.parent.copy() if self.parent else None
        root_copy = Choice(parent_copy, self.index_in_parent, self.id, self.name, self.max_delay)
        root_copy.set_children([child.copy() for child in self.children] if self.children else [])
        return root_copy

    def to_dict(self) -> dict:
        base = {"max_delay": self.max_delay}
        base.update(super().to_dict())
        return base


class Nature(ExclusiveGateway):
    def __init__(self, parent: Gateway, index_in_parent: int, id: int, name: str, distribution: list[float]) -> None:
        super().__init__(parent, index_in_parent, id, name)
        self.distribution = np.array(self._normalize_distribution(distribution), dtype=np.float64)

    @staticmethod
    def _normalize_distribution(distribution: list[float], precision: int | None = None) -> list[float]:
        values = np.asarray(distribution, dtype=np.float64)
        if values.size == 0:
            return []
        if values.size == 1:
            return [1.0]
        values = values.copy()
        values[-1] = 1.0 - np.sum(values[:-1], dtype=np.float64)
        decimals = np.finfo(np.float64).precision if precision is None else precision
        values = np.round(values, decimals=decimals)
        values[-1] = np.round(1.0 - np.sum(values[:-1], dtype=np.float64), decimals=decimals)
        return values.tolist()

    def dot(self):
        return f'\n node_{self.id}[shape=diamond label="{self.name} id:{self.id}" style="filled" fillcolor=yellowgreen];'

    def copy(self) -> 'Nature':
        parent_copy = self.parent.copy() if self.parent else None
        root_copy = Nature(parent_copy, self.index_in_parent, self.id, self.name, self.distribution)
        root_copy.set_children([child.copy() for child in self.children] if self.children else [])
        return root_copy

    def to_dict(self) -> dict:
        base = {"distribution": self.distribution.tolist()}
        base.update(super().to_dict())
        return base


class Loop(ExclusiveGateway):
    def __init__(self, parent: Gateway, index_in_parent: int, id: int, name: str, probability: float,
                 bound: int) -> None:
        super().__init__(parent, index_in_parent, id, name)
        self.bound = bound
        self.probability = np.float64(probability)

    @overrides
    def set_children(self, children) -> None:
        if len(children) != 1:
            raise ValueError("Loop must have exactly one child")

        super().set_children(children)

    @overrides
    def to_dict(self) -> dict:
        base = {"distribution": float(self.probability), "bound": self.bound}
        base.update(super().to_dict())
        return base

    def dot(self):
        return f'\n node_{self.id}[shape=diamond label="{self.name} id:{self.id}" style="filled" fillcolor=yellowgreen];'

    def copy(self) -> 'Loop':
        parent_copy = self.parent.copy() if self.parent else None
        root_copy = Loop(parent_copy, self.index_in_parent, self.id, self.name, self.probability, self.bound)
        root_copy.set_children([child.copy() for child in self.children] if self.children else [])
        return root_copy


class Task(ParseNode):
    def __init__(self, parent: 'Gateway', index_in_parent: int, id: int, name: str, impact: list,
                 duration: int) -> None:
        super().__init__(parent, index_in_parent, id)
        self.name = name
        self.impacts = np.array(impact, dtype=np.float64)
        self.duration = duration

    def dot(self):
        return f'\n node_{self.id}[label="{self.name}\n{self.impacts}\ndur:{self.duration} id:{self.id}" shape=rectangle style="rounded, filled" fillcolor=lightblue];'

    def copy(self) -> 'Task':
        parent_copy = self.parent.copy() if self.parent else None
        return Task(parent_copy, self.index_in_parent, self.id, self.name, self.impacts.tolist().copy(), self.duration)

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "label": self.name,
            "impacts": self.impacts.tolist(),
            "duration": self.duration,
        })
        return base

    def to_dict_id_node(self) -> dict:
        return {self.id: self}
