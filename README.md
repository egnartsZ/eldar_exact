# Boolean text search using Eldar
Fork of kerighan/eldar to adapt it to work on multiword queries with wildcards and fuzzy matching using lemmatization 
Also allows to retrieve indexes of matching substring in the text


## Getting Started

###

Installation:

```pip install eldar_exact```

### Basic usage

```python
from eldar_exact import Query, SearchQuery

# build list
documents = [
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien"]

eldar = Query('("gandalf" OR "frodo") AND NOT ("movie" OR "adaptation")')

# use `filter` to get a list of matches:
print(eldar.filter(documents))
# >>> ["Gandalf is a fictional character in Tolkien's The Lord of the Rings",
#     'Frodo is the main character in The Lord of the Rings']

# call to see if the text matches the query:
print(eldar(documents[0]))
# >>> True

# by default, words must match. Thus, "movie" != "movies":
print(eldar(documents[2]))
# >>> True

searchquery = SearchQuery('("gandalf is a" OR "frodo") OR ("gan*lf in")', ignore_case=True)
print(searchquery(documents[0]))
# >>> [<eldar_extended.Match object; span=(0, 12), match = 'gandalf is a'>]
print(searchquery(documents[1]))
# >>> [<eldar_extended.Match object; span=(0, 5), match = 'frodo'>]
print(searchquery(documents[4]))
# >>> []
```


You can also use it to mask Pandas DataFrames:

```python
from eldar_exact import Query
import pandas as pd

# build dataframe
df = pd.DataFrame([
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien"],
    columns=['content'])

# build query object
eldar = Query('("gandalf" OR "frodo") AND NOT ("movie" OR "adaptation")')

# eldar's call returns True if the text matches the query.
# You can filter a dataframe using pandas mask syntax:
df = df[df.content.apply(eldar)]
print(df)
```

### Parameters

There are four parameters that you can adjust in the query builder.
By default:
```python
Query(..., ignore_case=True, ignore_accent=True, exact_match=True, lemma_match = False, stop_words = False, stop_words_list = [], language = "en")
```
Let the query be ```query = '"movie"'```:

* If `ignore_case` is True, the documents "Movie" and "movie" will be matched. If False, only "movie" will be matched. 
* If `ignore_accent` is True, the documents "mövie" will be matched.
* If `exact_match` is True, the document will be tokenized and the query terms will have to match exactly. If set to False, the documents "movies" and "movie" will be matched. Setting this option to True may slow down the query.
* If `lemma_match` is True, the document and queries will be lemmatized and punctuation will be ignored. If set to True, the documents "be a wizard" and "is a wizard" will be matched. 
* If `stop_words` is True, the document and queries will be stripped of stopwords.
* `language` is used to chose the most appropriate lemmatizer and standard stop words. Currently allows `"fr"` or `"en"`.
* `stop_words_list` allows to custom the stop words used by the algorithm.


There are two types of queries:
* SearchQuery will return a list of match objects containing indices of all matched elements of the document
* Query will return a boolean if document contain the query


### Wildcards

All queries also support `*` as wildcard character. Wildcard matches any number (including none) of alphanumeric characters.

```python
from eldar_exact import Query

# sample document and query with multiple wildcards:
document = "Gandalf is a fictional character in Tolkien's The Lord of the Rings"
eldar = Query('"g*dal*"')

# call to see if the text matches the query:
print(eldar(document))
# >>> True
```


### Operators

Queries support different operators to build complex requests :
* `OR` 
* `AND`, `AND NOT` and `NOT` for Query objects
* `IF` for SearchQuery objects to only return indices which match the Query defined after IF



## Building an index for faster queries

Searching in a large corpus using the Query object is slow, as each document has to be checked.
For (much) faster queries, create an `Index` object, and build it using a list of documents.

```python
from eldar import Index

documents = [
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien",
    "Frodo Baggins is a hobbit"
]

index = Index(ignore_case=True, ignore_accent=True)
index.build(documents)  # must only be done once

# persist and retrieve index from disk
index.save("index.p")  # but documents are copied to disk
index = Index.load("index.p")

print(index.search('"frodo b*" AND NOT hobbit'))  # support wildcards
print(index.count('"frodo b*" AND NOT hobbit'))  # shows only the count
# to only return document ids, set `return_ids` to True:
print(index.search('"frodo b*" AND NOT hobbit', return_ids=True))
```

It works like a usual search engine does: by keeping a dictionary that maps each word to its document ids. The boolean query is turned into an operation tree, where document ids are joined or intersected in order to return the desired matches.




## License

This package is MIT licensed.
