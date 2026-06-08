class truc:
    att1: list[int]
    def __init__(self) -> None:
        self.att1 = []

class trucPlus(truc):
    def __init__(self) -> None:
        super().__init__()
        self.att1.append(10)

obj = trucPlus()
print(obj.att1)