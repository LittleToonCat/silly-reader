from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

name2icon = {
            "Overjoyed Laff Meters": 'resources/icons/sillymeter_laffteam.png',
            "Decreased Fish Rarity": 'resources/icons/sillymeter_fishteam.png',
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

def drawText(layer, xy, text, fill=None, drawer = None, fontPath='resources/ImpressBT.ttf', size=50):
    font = ImageFont.truetype(fontPath, size)
    x, y = xy

    shadowLayer = Image.new('RGBA', layer.size, (255, 255, 255, 0))

    shadowDrawer = ImageDraw.Draw(shadowLayer)

    shadowDrawer.text((x+2, y+2), text, fill='black', font=font)

    shadowLayer.filter(ImageFilter.BLUR)

    layer = Image.alpha_composite(layer, shadowLayer)

    drawer = ImageDraw.Draw(layer)

    drawer.text(xy, text, fill=fill, font=font)
    return Image.alpha_composite(layer, layer)

def drawMultilineText(layer, xy, texts, fill=None, drawer = None, fontPath='resources/ImpressBT.ttf', size=50, align='left'):

    font = ImageFont.truetype(fontPath, size)
    x, y = xy

    shadowLayer = Image.new('RGBA', layer.size, (255, 255, 255, 0))

    shadowDrawer = ImageDraw.Draw(shadowLayer)

    shadowDrawer.multiline_text((x+2, y+2), texts, fill='black', font=font, align=align)

    shadowLayer.filter(ImageFilter.BLUR)

    layer = Image.alpha_composite(layer, shadowLayer)

    drawer = ImageDraw.Draw(layer)

    drawer.multiline_text(xy, texts, fill=fill, font=font, align=align)
    return Image.alpha_composite(layer, layer)

def createActiveImage(rewards, asOf):
    background = Image.open('resources/template.png').convert('RGBA')
    out = drawText(background, (417, 23), 'The Silly Meter is active!', fill=(255, 187, 87))
    out = addActiveRewards(out, rewards)
    out = addFooter(out, asOf)
    return out

def addActiveRewards(out, rewards):
    layer = Image.new('RGBA', out.size, (255, 255, 255, 0))

    xOffset = 0

    for name in rewards:
        iconPath = name2icon.get(name, 'resources/icons/sillymeter_unknown.png')
        rewardIcon = Image.open(iconPath).convert('RGBA').resize((150, 150))
        layer.paste(rewardIcon, (246 + xOffset, 259))
        xOffset += 350

    xOffset = 0

    for name in rewards:
        layer = drawMultilineText(layer, (200 + xOffset, 425), textwrap.fill(name, width=15), fill=(255, 187, 87), size=40,
                                  align='center')
        xOffset += 350

    return Image.alpha_composite(out, layer)


def addFooter(out, asOf):
    layer = Image.new('RGBA', out.size, (255, 255, 255, 0))
    reader = Image.open('resources/sillyreader.png').convert('RGBA')
    layer.paste(reader, (25, 544))

    layer = drawText(layer, (200, 669), asOf.strftime('Last Updated: %a, %b %-d %Y, %-I:%M %p Toontown Time'), size=40)

    out = Image.alpha_composite(out, layer)
    return out

if __name__ == "__main__":
    import random
    from datetime import datetime
    from pytz import timezone

    # Ensure that the 3 awards are unique.
    rewards = set()
    while len(rewards) < 3:
        rewards.add(random.choice(list(name2icon.keys())))

    out = createActiveImage(rewards, datetime.now(timezone('US/Pacific')))
    out.show()
    out.save('Test.png')
