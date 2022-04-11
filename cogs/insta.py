from __future__ import unicode_literals
import discord
from discord.ext import commands
import instaloader
from instaloader import Post
import youtube_dl
import re
import os
import json
import requests
from lxml import html
import io
import magic
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio


class Insta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.insta = instaloader.Instaloader(download_video_thumbnails=False)
        insta_creds = json.load(open("./auth.json"))
        self.insta.login(insta_creds["username"], insta_creds["password"])
    @commands.Cog.listener()
    async def on_message(self, message):
        if(message.author.id == 416391123360284683):
            return
        shortcode = re.search('(https://.*)/(.*)/', message.content)
        link = re.search('(https://.*/.*/.*)', message.content)
        if shortcode is None:
            return

        directory = os.fsencode("./instagram/")
        # Empty the image directory of old images
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            os.remove(filepath)
        if "instagram" not in shortcode.group(1) \
                and "deviantart" not in shortcode.group(1) \
                and "twitter" not in shortcode.group(1)\
                and "artfight" not in shortcode.group(1):
            return
        # Create and download the post
        if "instagram" in shortcode.group(1):
            await instagram_rip(self, shortcode, message)
        elif "deviantart" in shortcode.group(1):
            await deviantart_rip(self, message, link)
            return
        elif "twitter" in shortcode.group(1):
            await twitter_rip(self, message)
        elif "artfight" in shortcode.group(1):
            await artfight_rip(self, message)
            return
        filepath = None
        try:
            # Delete all downloaded files that aren't the image
            for filename in os.listdir(directory):
                name = filename.decode('utf-8')
                if name.endswith(".jpg") or name.endswith(".png") or name.endswith(".mp4"):
                    print(f"not deleting {filename}")
                    pass
                else:
                    filepath = os.path.join(directory, filename)
                    os.remove(filepath)
        except Exception as e:
            await message.channel.send(f"Unable  to clean the directory after downloading images; error is {e}")
            return

        # Send all downloaded images into chat
        for filename in os.listdir(directory):
            print(f"filename is {filename}.")
            try:
                filepath = os.path.join(directory, filename)
                if link.group(0) is not None and await is_spoiler(message):
                    photo = discord.File(fp=filepath, filename=filename.decode('utf-8'), spoiler=True)
                else:
                    photo = discord.File(fp=filepath, filename=filename.decode('utf-8'))
                await message.channel.send(file=photo)
            except Exception as e:
                await message.channel.send(f"Unable to send media; error is {e}")
                continue

async def instagram_rip(self, shortcode, message):
    try:
        async with message.channel.typing():
            post = Post.from_shortcode(self.insta.context, shortcode.group(2))
            self.insta.download_post(post, "instagram")
            return True
    except TypeError:
        return False
    except Exception as e:
        await message.channel.send(f"Unable to download instagram post; error is {e}")
        return False

async def deviantart_rip(self, message, link):
    try:
        async with message.channel.typing():
            # Retrieve image link
            page = requests.get(link[1])
            raw_html = html.fromstring(page.content)
            image = raw_html.xpath('//*[@id="root"]/main/div/div[1]/div[1]/div/div[2]/div[1]/div/img/@src')
            title = raw_html.xpath('//*[@id="root"]/main/div/div[1]/div[1]/div/div[2]/div[1]/div/img/@alt')

            await direct_download(image, title, message, "deviantart")
            return True
    except Exception as e:
        await message.channel.send(f"Unable to download deviantart post; error is {e}")
        return False

async def twitter_rip(self, message):
    try:
        twitter_link = re.search('(https://twitter.com/[a-zA-Z0-9_]*/status/[0-9]*)', message.content).group(1)
        ydl_ops = {'outtmpl': 'instagram/%(title)s.%(ext)s'}
        with youtube_dl.YoutubeDL(ydl_ops) as ydl:
            print(twitter_link)
            ydl.download([f'{twitter_link}'])
        return True
    except youtube_dl.utils.DownloadError:
        pass
    except TypeError:
        return False
    except Exception as e:
        print(f"Unable to download tweet; error is {e}")
        return False

async def artfight_rip(self, message):
    artfight_creds = json.load(open("./auth.json"))
    options = Options()
    options.headless = True
    browser = webdriver.Chrome(options=options)
    browser.get(message.content)
    username = browser.find_element_by_xpath("//input[@name='username']")
    password = browser.find_element_by_xpath("//input[@name='password']")
    username.send_keys(artfight_creds["artuser"])
    password.send_keys(artfight_creds["artpass"])
    password.submit()
    await asyncio.sleep(5)
    image = browser.find_element_by_css_selector('div div a img').get_attribute("src")
    title = browser.find_element_by_css_selector('div div a img').get_attribute("data-original-title")
    await direct_download(image, title, message, "artfight")
    browser.quit()
    return True

async def direct_download(image, title, message, site):
    image_request = None
    if site == "deviantart":
        # Check if image response list is empty
        if not image:
            unsupported = await message.channel.send("Unable to retrieve link; likely a currently unsupported video.")
            time.sleep(5)
            await unsupported.delete()
            return
        # Get raw image data from link
        image_request = requests.get(image[0], stream=True).raw.data
    elif site == "artfight":
        image_request = requests.get(image, stream=True).raw.data
    # Find file extension
    filetype = magic.Magic(mime=True).from_buffer(image_request)
    filetype = filetype.split('/')[1]

    # Convert into discord file
    raw_image = io.BytesIO(image_request)
    if site == "deviantart":
        title = title[0]
    if(await is_spoiler(message)):
        discord_file = discord.File(fp=raw_image, filename=title + '.' + filetype, spoiler=True)
    else:
        discord_file = discord.File(fp=raw_image, filename=title + '.' + filetype)
    await message.channel.send(file=discord_file)
    await message.edit(suppress=True)
    print(f"Successfully posted image {title}.")


# Pass in the message and the link string to check for spoiler
async def is_spoiler(message):
    spoil = False
    spoiler = re.findall('(\|\|([^|]*)\|\|)', message.content)
    link = re.search('((https://.*)(/.*/)([\w-]*)+)', message.content)
    for match in spoiler:
        if spoiler is not None and link is not None and match[1] == link.group(1):
            spoil = True
    if spoil:
        return True
    else:
        return False


def setup(bot):
    bot.add_cog(Insta(bot))

