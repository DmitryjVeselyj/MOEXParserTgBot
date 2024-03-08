from abc import ABCMeta


class MoexObject:
    __metaclass__ = ABCMeta

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return str(self)

    def __getitem__(self, item: str):
        return self.__dict__[item]
