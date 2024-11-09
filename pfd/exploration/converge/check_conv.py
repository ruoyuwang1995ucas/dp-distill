from abc import ABC, abstractmethod
from pathlib import Path


class CheckConv(ABC):
    __ConvCheckers = {}

    @staticmethod
    def register(key: str):
        """Register a model interface. Used as decorators

        Args:
            key (str): key of the model
        """

        def decorator(object):
            CheckConv.__ConvCheckers[key] = object
            return object

        return decorator

    @staticmethod
    def get_checker(key: str):
        """Get a checker for CheckConv

        Args:
            key (str): _description_

        Raises:
            RuntimeError: _description_

        Returns:
            _type_: _description_
        """
        try:
            return CheckConv.__ConvCheckers[key]
        except KeyError as e:
            raise RuntimeError("unknown driver: " + key) from e

    @staticmethod
    def get_checkers() -> dict:
        """Get all filters

        Returns:
            dict: all filters
        """
        return CheckConv.__ConvCheckers

    @abstractmethod
    def check_conv(self):
        pass

    @classmethod
    @abstractmethod
    def doc(cls):
        return "The default method doc"

    @classmethod
    @abstractmethod
    def args(cls):
        """
        The default arguments for the method
        """
        return []