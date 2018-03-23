# Jeeves
  
This project is a Chatbot. My goal is to make him intelligent.
  
## Installation

First copy .env.dist and fill in missing values (slack token)

### Using docker

- Run docker-compose build
- Run docker-compose up
  
### By hand
  
Requirements : Python / Redis

- Install python (google it)
- Install redis (apt-get install redis-server)
- Run redis-server
- Initialize basic data (copy data/dump.rdb in your redis dir)
- Install pip (apt-get install -y python3-pip)
- Run pip install -r requirements.txt
- Run python -c "import nltk; nltk.download()" (when prompted to select a package choose "all")
- Run python . if you want to talk to Jeeves
- Run python slack.py if you want to add Jeeves to slack (you will need to add a bot then create the environment variable SLACK_BOT_TOKEN with the token slack provides)

## Usage

You can talk to Jeeves in a regular way but if you want him to learn something, there are some specific keywords to tell him:
* If your sentence contains "did you learn", Jeeves will tell you the top 25 words he learned ordered by frequency
  * Example: "Hey Jeeves, what did you learn today?"
* If your sentence contains "please forget " and is followed by a list of words separated by ", ", Jeeves will erase the words you gave him from his memory.
  * Example: "Jeeves, could you please forget annihilation, human, race?"
* If your sentence contains "please ignore " and is followed by a list of words separated by ", ", Jeeves will add the words you gave him to his ignore list and won't react to them.
  * Example: "Hi, please ignore cheated, wife"
* If your sentence contains "list all " and is followed by the name of one of Jeeves' memories ("reactions", "new words", "words", "ignored words"), Jeeves will list all the words contains in the memory (careful, this has no limit)
  * Example: "Hey Jeeves, could you list all new words?"
* If your sentence contains "please add ", is followed by a list of words separated by ", " then by " to ", then by a reaction Jeeves already know, Jeeves will add the words you gave him to this reaction.
  * Example: "Hey Jeeves, can you please add vodka, marijuana to party?"
  
## Incoming features
* You can now learn Jeeves how to react to certain words
* Jeeves now randomly asks you to teach him things he doesn't understand
