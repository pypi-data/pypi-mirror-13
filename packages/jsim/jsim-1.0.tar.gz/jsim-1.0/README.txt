This package uses Jaccard similarity with bag of words to find similarities between passed in contents
and a json file.

There are two useful functions:

save(filename, docID, contents)  ===> takes in the json filename, an id for the document you want to save,
									  and the contents of the document in a string. The function adds on 
									  the docID and contents to filename, and if filename doesn't exist, it 
									  creates a new file and inserts the passed in contents.

def getSimilarities(filename, docID, contents, threshold)  ===> takes in the filename of all the documents to 
																to compare to, docID of the document you want 
																to find similarities for, the contents of the
																document, a similarity threshold between 0 and
																1 inclusive. The function returns a list of 
																(similarity, docID) in descending order of all
																documents whose similarities are above or equal
																to the threshold.