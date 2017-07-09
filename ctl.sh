if [ "$#" != 1 ]; then
	echo "Usage: ./ctl start/stop"
	exit -1
fi

if [ "$1"x = "start"x ]; then
	NLTK_DATA="/var/nltk_data/" nohup python3 app.py > nohup.log 2>&1 &
elif [ "$1"x = "stop"x ]; then
	curl "http://tools.eflclub.me/shutdown"
else
	echo "Usage: ./ctl start/stop"
fi