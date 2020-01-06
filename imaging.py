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

name2desc = {
            "Overjoyed Laff Meters": 'A little joy goes a long way! +8 Maximum Laff Points while the Silly Meter is maxed.',
            "Decreased Fish Rarity": 'Holy Mackerel! Rare fish are easier to find with this silly perk.',
            "Double Jellybeans": 'Double your fun (and money) with double jellybeans for all activities!',
            "Speedy Garden Growth": 'Make your gardens bloom faster than Daisy\'s to ramp up your garden experience.',
            "Double Racing Tickets": 'Ready, set, GO get Double Tickets at Goofy Speedway! Doesn\'t apply to Grand Prix races.',
            "Global Teleport Access": 'Who needs ToonTasks? Temporarily unlock teleport access to all areas of Toontown!',
            "Doodle Trick Boost": 'Jump! Backflip! Dance! Doodles perform tricks more often and earn more experience.',
            "Double Toon-Up Experience": 'Earn double experience for Toon-Up gags in all battles!',
            "Double Trap Experience": 'Earn double experience for Trap gags in all battles!',
            "Double Lure Experience": 'Earn double experience for Lure gags in all battles!',
            "Double Sound Experience": 'Earn double experience for Sound gags in all battles!',
            "Double Throw Experience": 'Earn double experience for Throw gags in all battles!',
            "Double Squirt Experience": 'Earn double experience for Squirt gags in all battles!',
            "Double Drop Experience": 'Earn double experience for Drop gags in all battles!',
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

def createActiveImage(rewards, asOf):
    background = Image.open('resources/template.png').convert('RGBA')
    out = drawText(background, (417, 23), 'The Silly Meter is active!', fill=(255, 187, 87))
    out = drawText(out, (280, 143), 'You can now vote for the following Silly Teams:', fill=(255, 187, 87), size=40)
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

    out = Image.alpha_composite(out, layer)

    xOffset = 0

    for name in rewards:
        out = drawMultilineText(out, (200 + xOffset, 425), textwrap.fill(name, width=15), fill=(255, 187, 87), size=40,
                                  align='center')

        desc = name2desc.get(name, '???')
        out = drawMultilineText(out, (230 + xOffset, 525), textwrap.fill(desc, width=25), fill=(255, 187, 87), size=20,
                                  align='center')
        xOffset += 350

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

    out = createActiveImage(rewards, datetime.now(timezone('US/Pacific')))
    # out.show()
    out.save('Test.png')
