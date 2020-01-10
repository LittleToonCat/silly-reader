#!/usr/bin/python3
import configparser, requests, pause, time, os, logging
from datetime import datetime
from pytz import timezone, utc

import imaging

config = configparser.ConfigParser()
# Read the config file.
# TODO: Pass the file name through argparse
config.read('config.ini')

USING_TWITTER = False
USING_MASTODON = False

if 'Twitter' in config:
    USING_TWITTER = True
    twitterConfig = config['Twitter']

    import twitter
    twitterApi = twitter.Api(consumer_key=twitterConfig['ConsumerKey'],
                             consumer_secret=twitterConfig['ConsumerSecret'],
                             access_token_key=twitterConfig['AccessToken'],
                             access_token_secret=twitterConfig['AccessSecret'])

if 'Mastodon' in config:
    USING_MASTODON = True
    mastodonConfig = config['Mastodon']

    from mastodon import Mastodon
    mastodonApi = Mastodon(api_base_url=mastodonConfig['ApiUrl'],
                           client_id=mastodonConfig['ClientKey'],
                           client_secret=mastodonConfig['ClientSecret'],
                           access_token=mastodonConfig['AccessToken'])


POST_UPDATES = config['General'].getboolean('PostUpdates')
PRINT_TEXT = config['General'].getboolean('PrintOutput')
CREATE_IMAGES = config['General'].getboolean('CreateImages')

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

def createImageForStatus(response):
    state = response['state']
    console.info(f'Creating image for {state}...')
    if state == 'Active':
        return imaging.createActiveImage(response['rewards'], datetime.fromtimestamp(response['asOf'], zone))
    elif state == 'Reward':
        return imaging.createRewardImage(response['winner'], datetime.fromtimestamp(response['nextUpdateTimestamp'], zone), datetime.fromtimestamp(response['asOf'], zone))
    elif state == 'Inactive':
        return imaging.createInactiveImage(response['rewards'], datetime.fromtimestamp(response['nextUpdateTimestamp'], zone), datetime.fromtimestamp(response['asOf'], zone))

    return None

def postUpdate(response, message, replyMessage = ''):
    # Bring up the 'lastState' file.  It is used to determine whether or not the state
    # have been updated since the previous API calls.
    state = response['state']
    if os.path.exists('lastState'):
        lastState = open('lastState', 'r').read().rstrip()
    else:
        lastState = ''

    if not POST_UPDATES or state == lastState:
        return

    console.info(f'"{state}" is different than "{lastState}", posting...')

    if CREATE_IMAGES:
        image = createImageForStatus(response)
        if image:
            image.save('image.png')
        else:
            console.warning(f'Don\'t know what to create image for state "{state}"!')
            image = None
    else:
        image = None

    if USING_TWITTER:
        console.info('Tweeting...')
        if image:
            console.info('Uploading image to Twitter...')
            status = twitterApi.PostUpdate(message, 'image.png')
        else:
            status = twitterApi.PostUpdate(message)
        console.info(f'Tweeted, {status}')
        if replyMessage:
            replyStatus = twitterApi.PostUpdate(replyMessage, in_reply_to_status_id=status.id)
            console.info(f'Reply tweeted. {replyStatus}')

    if USING_MASTODON:
        console.info('Tooting...')
        if image:
            console.info('Uploading image to Mastodon...')
            status = mastodonApi.status_post(message, media_ids=mastodonApi.media_post('image.png', 'image/png'))
        else:
            status = mastodonApi.status_post(message)
        console.info(f'Tooted, {status}')
        if replyMessage:
            replyStatus = mastodonApi.status_post(replyMessage, in_reply_to_id=status)
            console.info(f'Reply tooted. {replyStatus}')

    open('lastState', 'w').write(state)

# Main loop
while True:
    # Call the endpoint.
    r = requests.get(url, headers)

    if r.status_code == 200:
        # Convert the json response into a dict.
        response = r.json()

        console.info(f'Response from web server: {response}')

        if int(time.time()) >= response['nextUpdateTimestamp']:
            # The web server might not have updated yet... Pause for 20 seconds before trying again.
            console.warning(f"{int(time.time())} is ahead of {response['nextUpdateTimestamp']}, pausing for 20 seconds...")
            pause.seconds(20)
            continue

        # Setup datetimes for the nextUpdateTime and asOf timestamps respectivly.
        nextUpdateTime = datetime.fromtimestamp(response['nextUpdateTimestamp'], zone)
        asOf = datetime.fromtimestamp(response['asOf'], zone)

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
            text = f"The {winner} reward is now active throughout Toontown!\n\n"
            text += nextUpdateTime.strftime('The reward will last until %a, %b %-d %Y, %-I:%M %p Toontown Time.')
        elif state == 'Inactive':
            text = "The reward has ended and the The Silly Meter is now cooling down.\n\n"
            text += nextUpdateTime.strftime('It will start up again on %a, %b %-d %Y, %-I:%M %p Toontown Time.')

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
            console.info(text)
            if replyText:
                console.info(replyText)

        postUpdate(response, text, replyText)
        pause.until(datetime.fromtimestamp(response['nextUpdateTimestamp'] + 20))
    else:
        # uhhhhhhh abormity two???
        now = datetime.now(zone)
        text = now.strftime(f"Abnormity??? The web server has returned a {r.status_code} error code when trying to get Silly Meter status at %a, %b %-d %Y, %-I:%-M %p Toontown Time\n\n")
        text += "Trying again in 5 minutes."
        console.warning(text)

        postUpdate({'state': r.status_code}, text)
        pause.minutes(5)
