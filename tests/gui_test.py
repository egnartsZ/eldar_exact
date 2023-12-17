import pandas as pd
from eldar_exact import Index

documents = [
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien",
    "Frodo Baggins is a hobbit"
]
df = pd.DataFrame(documents, columns=["content"])
df["number"] = range(len(documents))

index = Index()
index.build(df, column="content")
index.gui()  # QT interface
# print(index.search("frodo"))
