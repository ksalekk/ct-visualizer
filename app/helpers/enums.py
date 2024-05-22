from enum import Enum


class Plain(Enum):
    XY = "XY"
    XZ = "XZ"
    YZ = "YZ"

    # # along, horizontal, vertical axis
    # @staticmethod
    # def get_axes_names(plain):
    #     if plain == Plain.XY:
    #         return Axis.Z, Axis.X, Axis.Y
    #     elif plain == Plain.XZ:
    #         return Axis.Y, Axis.X, Axis.Z
    #     elif plain == Plain.YZ:
    #         return Axis.X, Axis.Y, Axis.Z
    #     else:
    #         raise Exception()


# class Axis(Enum):
#     X = "X"
#     Y = "Y"
#     Z = "Z"


class Location(Enum):
    TOP = "Top"
    BOTTOM = "Bottom"
    LEFT = "Left"
    RIGHT = "Right"
    CENTER = "Center"
    TOP_LEFT = "Top Left"
    TOP_RIGHT = "Top Right"
    BOTTOM_LEFT = "Bottom Left"
    BOTTOM_RIGHT = "Bottom Right"
