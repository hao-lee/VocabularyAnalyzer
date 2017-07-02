# Phonetic Transcription Interpreter

This is a useful tool, especially when you practice your pronunciation. It can scan the text and generate corresponding phonetic transcription, so I think it would be perfect to name it "Phonetic Transcription Interpreter".

I hope you will enjoy it. Thanks.

### Requirements:

* Python >= 3.4 (3.5 is recommended)
* [Flask](http://flask.pocoo.org/docs/0.12/installation/)
* [gevent](http://www.gevent.org/intro.html#installation-and-requirements)
* [Requests](http://docs.python-requests.org/en/master/user/install/#install)
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)
* [lxml](http://lxml.de/installation.html#installation)
* [NLTK](http://www.nltk.org/install.html)
* [NLTK Data](http://www.nltk.org/data.html)
	> **These individual NLTK Data packages is needed:**
	>
	> averaged_perceptron_tagger
	>
	> punkt
	>
	> tagsets
	>
	> wordnet
	>
	> Note: If you install data packages to a custom location, you will need to set the NLTK_DATA environment variable to specify the location of the data.
	>
	> For example: `NLTK_DATA="/var/nltk_data/" python3 app.py`