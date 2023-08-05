from .mechanics import ControllerMechanics
from .utils import ControllerUtils
from .virtual import ControllerVirtuals


class Controller(
    ControllerMechanics,
    ControllerUtils,
    ControllerVirtuals,
):
    pass
