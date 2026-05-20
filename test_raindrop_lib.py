import inspect
from raindropiopy import Raindrop

print(
    f"Raindrop class methods: {inspect.getmembers(Raindrop, predicate=inspect.isroutine)}"
)
