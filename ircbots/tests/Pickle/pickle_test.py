import pickle

output = open('tastyPickle.pkl','wb')

pickle.dump("tastes like pickle", output)

#fuck pickle lets shelve

output.close
