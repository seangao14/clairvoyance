# clairvoyance
project for Liquid Hacks 2020 - built in 42 hours

web app is live at http://clairvoyance.space/

Clairvoyance is a web application that uses a deep learning model to analyze win probabilities in League of Legends.

Data is pulled from challengers players on the NA server. (300 players, 100 matches per player, duplicate matches are thrown out. About 9000 total matches total)

Model architecture is a variably layered fully connected network, where the champion picks go through more layers than the other data. (this is the primary reason why a deep learning model was chosen over a traditional machine model)


## what is not included in this repo:
- Riot Games API key in clairvoyance/config.py
- training data. Data is too big to upload there is a data builder, although you need to obtain your own API key and tweak the time.sleep()s so that it does not exceed the rate limit. Training data should be located at clairvoyance/data/training, in .npy format. The notebooks will not run without the data.


Clairvoyance was created under Riot Games' "Legal Jibber Jabber" policy using assets owned by Riot Games. Riot Games does not endorse or sponsor this project.
