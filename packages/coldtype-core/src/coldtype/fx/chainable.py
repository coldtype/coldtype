
class Chainable():
    def __init__(self, func) -> None:
        self.func = func
    
    # def __or__(self, other):
    #     print("L HELLO")

    # def __ror__(self, other):
    #     print("R HELLO")