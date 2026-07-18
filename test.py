"""
probleme avec Etoile Filante
probleme avec medium
probleme avec divorce
probleme avec burnout

probleme avec chance (en fin de partie)
"""
def write(file_name: str, data):
    with open(file_name, "w") as file:
        file.write(str(data))

class A:
    def methode(self) ->dict:
        return {"a":1}

class B:
    def methode(self):
        return {}

class C(A, B):
    def methode(self):
        # Appeler la méthode de A spécifiquement
        data = A.methode(self)
        # ou celle de B
        for key, value in B.methode(self).items():
            data[key] = value 
        data["c"] = 1
        return data

c = C()
res = c.methode()  # Affiche: A.methode() puis C.methode()
print(res)