# clairvoyance
project for Liquid Hacks 2020 - built in 42 hours. Further development of this project will be **[here](https://github.com/seangao14/clairvoyance2.0)**

The web app is live at http://clairvoyance.space/  
Note: our API rate limit is very limited, so if the site incurrs heavy traffic it may exceed the API rate limit. For reference, we are allowed 20/second, and 100/2 minutes. Each summoner look up uses about 12 API calls.

Clairvoyance is a web application that uses a deep learning model to analyze win probabilities in League of Legends.

Data is pulled from challengers players on the NA server. (300 players, 100 matches per player, duplicate matches are thrown out. About 9000 total matches total)

Model architecture is a variably layered fully connected network, where the champion picks go through more layers than the other data. (this is the primary reason why a deep learning model was chosen over a traditional machine model)


## what is not included in this repo:
- Riot Games API key in clairvoyance/config.py
- training data. Data is too big to upload. However, there is a data builder, although you need to obtain your own API key and tweak the time.sleep()s so that it does not exceed the rate limit. Training data should be located at clairvoyance/data/training, in .npy format. The notebooks will not run without the data although the model functions fine without it.
- bootstrap js in static/js
- ipython notebooks used for training


Clairvoyance was created under Riot Games' "Legal Jibber Jabber" policy using assets owned by Riot Games. Riot Games does not endorse or sponsor this project.
