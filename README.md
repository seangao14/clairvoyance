# clairvoyance
CLairvoyance is a web application that uses a deep learning model to analyze win probabilities in League of Legends.

Data is pulled from challengers players on the NA server. (300 players, 100 matches per player, duplicate matches are thrown out. About 9000 total matches total)

Model architecture is a variably layered fully connected network, where the champion picks go through more layers than the other data. (this is the primary reason why a deep learning model was chosen over a traditional machine model)
