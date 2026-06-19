from abc import ABC, abstractmethod
from PIL import Image


class GradientStyle(ABC):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @abstractmethod
    def render(self) -> Image.Image:
        ...
