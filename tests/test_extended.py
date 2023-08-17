from eldar_extended import Query, SearchQuery


# create list of documents to match:
documents = [
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien"]
# build query:
query = Query('(("gandalf is a" OR "frodo") OR ("gandalf * movies")) AND NOT ("Tolkien")', ignore_case= True)
# print query:
#query = Query('"gan*lf in"', ignore_case= True)
print(query)
# >>> ((("gandalf is a") OR ("frodo")) OR ("gan*lf in")) AND NOT ("tolkien")


# call to see if the text matches the query:
print(query(documents[0]))
# >>> False
print(query(documents[1]))
# >>> True
print(query(documents[2]))
# >>> True
print(query(documents[3]))
# >>> True
print(query(documents[4]))
# >>> False



document = "Gandalf is a fictional characters in Tolkien's The Lord of the Rings"
q1 = Query('"are fictionals characters"', exact_match = False, lemma_match= True, stop_words = True)
q2 = Query('("lord ring")', exact_match = False, lemma_match= True, stop_words = True)
# call to see if the text matches the query:
print(q1(document))
# >>> True
print(q2(document))
# >>> True

searchquery = SearchQuery('("gandalf is a" OR "frodo") OR ("gan*lf in")', ignore_case= True)
print(searchquery(documents[0]))
# >>> [<eldar_extended.Match object; span=(0, 12), match = 'gandalf is a'>]
print(searchquery(documents[1]))
# >>> [<eldar_extended.Match object; span=(0, 5), match = 'frodo'>]
print(searchquery(documents[2]))
# >>> [<eldar_extended.Match object; span=(25, 35), match = 'gandalf in'>]
print(searchquery(documents[3]))
# >>> [<eldar_extended.Match object; span=(24, 29), match = 'frodo'>]
print(searchquery(documents[4]))
# >>> []

searchquery = SearchQuery('(("gandalf is a" OR "frodo") OR "gan*lf in") IF ("lord" AND "rings")', ignore_case= True)
print(searchquery(documents[0]))
# >>> [<eldar_extended.Match object; span=(0, 12), match = 'gandalf is a'>]
print(searchquery(documents[1]))
# >>> [<eldar_extended.Match object; span=(0, 5), match = 'frodo'>]
print(searchquery(documents[2]))
# >>> []
print(searchquery(documents[3]))
# >>> []
print(searchquery(documents[4]))
# >>> []