#!/usr/bin/python3
import configparser, requests, pause, time, os, logging
from datetime import datetime
from pytz import timezone, utc

config = configparser.ConfigParser()
# Read the config file.
# TODO: Pass the file name through argparse
config.read('config.ini')

import twitter
twitterConfig = config['Twitter']

api = twitter.Api(consumer_key=twitterConfig['ConsumerKey'],
                  consumer_secret=twitterConfig['ConsumerSecret'],
                  access_token_key=twitterConfig['AccessToken'],
                  access_token_secret=twitterConfig['AccessSecret'])

TWEET_UPDATES = config['General'].getboolean('PostUpdates')
PRINT_TEXT = config['General'].getboolean('PrintOutput')

# The API endpoint to use to get Silly Meter infomation.
url = 'https://www.toontownrewritten.com/api/sillymeter'

# The Toontown Time zone.
zone = timezone('US/Pacific')

# HTTP headers to use when requesting HTTP calls to the endpoint.
headers = {
    'User-Agent': "The Silly Reader (@Silly_Meter)\n(Twitter account run & programmed by: @LittleToonCat)\nGitHub repository: https://github.com/LittleToonCat/silly-reader"
}

# Function to pass to logging to print time wih the Toontown time.
def customTime(*args):
        utc_dt = utc.localize(datetime.utcnow())
        converted = utc_dt.astimezone(zone)
        return converted.timetuple()

# Setup logging.
logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S PT",
                    level=logging.INFO)
logging.Formatter.converter = customTime

console = logging.getLogger(__name__)

# Main loop
while True:
    # Call the endpoint.
    r = requests.get(url, headers)

    if r.status_code == 200:
        # Convert the json response into a dict.
        response = r.json()

        console.info(f'Response from web server: {response}')

        if int(time.time()) >= response['nextUpdateTimestamp']:
            # The web server might not have updated yet... Pause for 30 seconds before trying again.
            console.warning(f"{int(time.time())} is ahead of {response['nextUpdateTimestamp']}, pausing for 30 seconds...")
            pause.seconds(30)
            continue

        # Setup datetimes for the nextUpdateTime and asOf timestamps respectivly.
        nextUpdateTime = datetime.fromtimestamp(response['nextUpdateTimestamp'], zone)
        asOf = datetime.fromtimestamp(response['asOf'], zone)

        # Bring up the 'lastState' file.  It is used to determine whether or not the state
        # have been updated since the previous API calls.
        if os.path.exists('lastState'):
            lastState = open('lastState', 'r').read().rstrip()
        else:
            lastState = ''

        # Blank reply update text, because somethings are too big for Twitter's 250 character limit
        # (see Inactive state for an example).
        replyText = ""

        state = response['state']
        if state == 'Active':
            text = "The Silly Meter is now active with the following Silly Teams:\n"
            for reward in enumerate(response['rewards'], start=1):
                text += f'\n{reward[0]}. {reward[1]}'
        elif state == 'Reward':
            winner = response['winner']
            text = f"The {winner} reward is now being active throughout Toontown!\n\n"
            text += nextUpdateTime.strftime('The reward will last until %a, %b %-d %Y, %-I:%M %p Toontown Time.')
        elif state == 'Inactive':
            text = "The reward has ended and the The Silly Meter is now cooling down.\n\n"
            text += nextUpdateTime.strftime('It will start up again on %a, %b %-d %Y, %-I:%M %p Toontown Time.')
            if response.get('rewards'):
                # We're continuing on from replyText (notice the no "\n" at the end of the inital post).
                replyText = "Here are the next upcoming Silly Teams:\n"
                for reward in enumerate(response['rewards'], start=1):
                    replyText += f'\n{reward[0]}. {reward[1]}'
        else:
            # uhhhhhhh abormity???
            text = f"Landed into an unknown state '{state}'\n\n....Abormity???\n"


        # Insert the "Last Updated" text at the very bottom of the update.
        if replyText:
            replyText += asOf.strftime('\n\nLast Updated: %a, %b %-d %Y, %-I:%M %p Toontown Time')
        else:
            text += asOf.strftime('\n\nLast Updated: %a, %b %-d %Y, %-I:%M %p Toontown Time')

        if PRINT_TEXT:
            # Print text output
            print(text)
            if replyText:
                print(replyText)

        if TWEET_UPDATES and not state == lastState:
            console.info(f"Status has changed from '{lastState}' to '{state}', tweeting...")
            open('lastState', 'w').write(state)
            status = api.PostUpdate(text)
            console.info(f'Tweeted. {status}')
            if replyText:
                replyStatus = api.PostUpdate(replyText, in_reply_to_status_id=status.id)
                console.info(f'Reply tweeted. {replyStatus}')

        pause.until(datetime.fromtimestamp(response['nextUpdateTimestamp'] + 30))
    else:
        # uhhhhhhh abormity two???
        now = datetime.now(zone)
        text = now.strftime(f"Abnormity??? The web server has returned a {r.status_code} error code when trying to get Silly Meter status at %a, %b %-d %Y, %-I:%-M %p Toontown Time\n\n")
        text += "Trying again in 5 minutes."
        console.warning(text)
        if TWEET_UPDATES and not r.status_code == lastState:
            open('lastState', 'w').write(r.status_code)
            api.PostUpdate(text)
            console.info(f'Tweeted. {status}')

        pause.minutes(5)
