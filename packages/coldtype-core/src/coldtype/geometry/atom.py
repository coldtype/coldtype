from coldtype.geometry.geometrical import Geometrical


class Atom(Geometrical):
    def __init__(self, x):
        self.x = x
    
    __hash__ = object.__hash__
    
    def __eq__(self, o):
        # TODO isclose?
        try:
            return self.x == o.x
        except AttributeError:
            return self.x == o

    def __repr__(self):
        return f"Atom({self.x})"

    def __getitem__(self, key):
        if key == 0:
            return self.x
        else:
            raise TypeError("Index must be 0")
    
    def __len__(self):
        return 1

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        else:
            raise IndexError(
                "Invalid index for atom assignment, must be 0")
    
    def reverse(self):
        return self