from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

name2icon = {
            "Overjoyed Laff Meters": 'resources/icons/sillymeter_laffteam.png',
            "Teeming Fish Waters": 'resources/icons/sillymeter_fishteam.png',
            "Double Jellybeans": 'resources/icons/sillymeter_beanteam.png',
            "Speedy Garden Growth": 'resources/icons/sillymeter_gardenteam.png',
            "Double Racing Tickets": 'resources/icons/sillymeter_racingteam.png',
            "Global Teleport Access": 'resources/icons/sillymeter_teleportteam.png',
            "Doodle Trick Boost": 'resources/icons/sillymeter_trickteam.png',
            "Double Toon-Up Experience": 'resources/icons/sillymeter_toonupteam.png',
            "Double Trap Experience": 'resources/icons/sillymeter_trapteam.png',
            "Double Lure Experience": 'resources/icons/sillymeter_lureteam.png',
            "Double Sound Experience": 'resources/icons/sillymeter_soundteam.png',
            "Double Throw Experience": 'resources/icons/sillymeter_throwteam.png',
            "Double Squirt Experience": 'resources/icons/sillymeter_squirtteam.png',
            "Double Drop Experience": 'resources/icons/sillymeter_dropteam.png',
}


def drawText(layer, xy, text, fill=None, drawer = None, fontPath='resources/ImpressBT.ttf', size=50, shadow=True):
    font = ImageFont.truetype(fontPath, size)
    x, y = xy

    if shadow:
        shadowLayer = Image.new('RGBA', layer.size, (255, 255, 255, 0))
        shadowDrawer = ImageDraw.Draw(shadowLayer)
        shadowDrawer.text((x+2, y+2), text, fill='black', font=font)
        layer = Image.alpha_composite(layer, shadowLayer)

    drawer = ImageDraw.Draw(layer)
    drawer.text(xy, text, fill=fill, font=font)
    return Image.alpha_composite(layer, layer)

def drawMultilineText(layer, xy, text, fill=None, drawer = None, fontPath='resources/ImpressBT.ttf', size=50, align='left',
                      shadow=True):

    font = ImageFont.truetype(fontPath, size)
    x, y = xy

    if shadow:
        shadowLayer = Image.new('RGBA', layer.size, (255, 255, 255, 0))
        shadowDrawer = ImageDraw.Draw(shadowLayer)
        shadowDrawer.multiline_text((x+2, y+2), text, fill='black', font=font, align=align)
        layer = Image.alpha_composite(layer, shadowLayer)

    drawer = ImageDraw.Draw(layer)

    drawer.multiline_text(xy, text, fill=fill, font=font, align=align)
    return Image.alpha_composite(layer, layer)

def createActiveImage(rewards, descs, asOf):
    background = Image.open('resources/active_background.png').convert('RGBA')
    out = drawText(background, (417, 23), 'The Silly Meter is active!', fill=(255, 187, 87))
    out = drawText(out, (280, 143), 'You can now vote for the following Silly Teams:', fill=(255, 187, 87), size=40)
    out = addRewardList(out, rewards, descs)
    out = addFooter(out, asOf)
    return out

def createRewardImage(rewardName, desc, nextUpdateTime, asOf):
    background = Image.open('resources/reward_background.png').convert('RGBA')
    out = drawText(background, (307, 23), 'The Silly Meter has reached the top!', fill=(255, 187, 87))
    out = drawText(out, (350, 100), 'The following Silly Reward is now active:', fill=(255, 187, 87), size=40)

    iconLayer = Image.new('RGBA', out.size, (255, 255, 255, 0))
    iconPath = name2icon.get(rewardName, 'resources/icons/sillymeter_unknown.png')
    rewardIcon = Image.open(iconPath).convert('RGBA').resize((150, 150))
    iconLayer.paste(rewardIcon, (626, 204))
    out = Image.alpha_composite(out, iconLayer)

    out = drawMultilineText(out, (599, 350), textwrap.fill(rewardName, width=15), fill=(255, 187, 87), size=40,
                              align='center')

    out = drawMultilineText(out, (599, 450), textwrap.fill(desc, width=25), fill=(255, 187, 87), size=20,
                              align='center')

    out = drawText(out, (250, 580), nextUpdateTime.strftime('The reward will last until %a, %b %-d %Y, %-I:%M %p Toontown Time'), fill=(255, 187, 87), size=30)

    out = addFooter(out, asOf)

    return out

def createInactiveImage(rewards, descs, nextUpdateTime, asOf):
    background = Image.open('resources/inactive_background.png').convert('RGBA')
    out = drawText(background, (300, 23), 'The Silly Meter is now cooling down.', fill=(255, 187, 87))
    out = drawText(out, (100, 100), nextUpdateTime.strftime('It will start up again on %a, %b %-d %Y, %-I:%M %p Toontown Time'), fill=(255, 187, 87), size=40)
    out = drawText(out, (350, 163), 'Here are the next upcoming Silly Teams:', fill=(255, 187, 87), size=40)
    out = addRewardList(out, rewards, descs)
    out = addFooter(out, asOf)
    return out

def addRewardList(out, rewards, descs):
    layer = Image.new('RGBA', out.size, (255, 255, 255, 0))

    xOffset = 0
    descCount = 0

    for name in rewards:
        iconPath = name2icon.get(name, 'resources/icons/sillymeter_unknown.png')
        rewardIcon = Image.open(iconPath).convert('RGBA').resize((150, 150))
        layer.paste(rewardIcon, (246 + xOffset, 259))
        xOffset += 350

    out = Image.alpha_composite(out, layer)

    xOffset = 0

    for name in rewards:
        out = drawMultilineText(out, (200 + xOffset, 425), textwrap.fill(name, width=15), fill=(255, 187, 87), size=40,
                                  align='center')

        desc = descs[descCount]
        out = drawMultilineText(out, (230 + xOffset, 525), textwrap.fill(desc, width=25), fill=(255, 187, 87), size=20,
                                  align='center')
        xOffset += 350
        descCount += 1

    return out

def addFooter(out, asOf):
    layer = Image.new('RGBA', out.size, (255, 255, 255, 0))
    reader = Image.open('resources/sillyreader.png').convert('RGBA')
    layer.paste(reader, (25, 544))
    out = Image.alpha_composite(out, layer)

    out = drawText(out, (200, 669), asOf.strftime('Last Updated: %a, %b %-d %Y, %-I:%M %p Toontown Time'), size=40)
    return out

if __name__ == "__main__":
    import random
    from datetime import datetime
    from pytz import timezone

    # Ensure that the 3 awards are unique.
    rewards = set()
    while len(rewards) < 3:
        rewards.add(random.choice(list(name2icon.keys())))

    out = createInactiveImage(rewards, datetime.now(timezone('US/Pacific')), datetime.now(timezone('US/Pacific')))
    # out.show()
    out.save('Test.png')
