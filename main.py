'''
MIT License

Copyright (c) 2024 spageektti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import discord
import os
import subprocess
from dotenv import load_dotenv
from googletrans import Translator

load_dotenv()
bot = discord.Bot()

if not os.path.exists("tldr"):
    subprocess.run(["git", "clone", "https://github.com/tldr-pages/tldr.git"])
else:
    subprocess.run(["cd", "tldr", "&&", "git", "pull"], shell=True)

languages = ['ar', 'bn', 'bs', 'ca', 'cs', 'da', 'de', 'es', 'fa', 'fi', 'fr', 'hi', 'id', 'it', 'ja', 'ko', 'lo', 'ml', 'ne', 'nl', 'no', 'pl', 'pt_BR', 'pt_PT', 'ro', 'ru', 'sh', 'sr', 'sv', 'ta', 'th', 'tr', 'uk', 'uz', 'zh', 'zh_TW']
guide = [
'',
'''
> **1. Copy the translation**
Copy the content of the translation as shown in the image below.
''',
'''
> **2. Create fork**
Go to [TLDR pages repo on GitHub](https://github.com/tldr-pages/tldr/) and press the button labeled *fork*.
''',
'''
> **3. Navigate to the right place**
Go to the directory `pages.{code of your language}`, and then to the directory where your file is located.
''',
'''
> **4. Create your file and paste content**
Press on *Add file*, then on *Create new file*. Type `name_command.md` as the file name. Then paste the content of your translation.
''',
'''
> **5. Commit changes to new branch**
Press the *Commit changes...* button. In the *Commit message* field, type `{command name}: add {Language Name} translation` for example `dart: add Polish translation`. Press *Create a new branch for this commit and start a pull request*.
''',
'''
> **6. Create a Pull Request**
Go back to the repository [tldr-pages/tldr](https://github.com/tldr-pages/tldr/) and press `Compare & pull request`. Select your branch and fill in the fields as shown in the image.
Congratulations! You have submitted your Pull Request! Thank you for helping us create TLDR Pages!
''',
]

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="translate_folder", description="Start translating TLDR pages folder")
async def translate_folder(ctx: discord.ApplicationContext, language:discord.Option(str), folder:discord.Option(str, choices=['android', 'common', 'freebsd', 'linux', 'netbsd', 'openbsd', 'osx', 'sunos', 'windows']), test:discord.Option(bool, default=False)):
    await ctx.respond("Hi! This bot will help you translate TLDR pages.")
    
    if not language in languages:
            await ctx.send(f'{language} is not a correct language code. Language codes:\n' + ', '.join([f'`{lang}`' for lang in languages]))
            return
    
    google_translate_language = language
    if(google_translate_language[:2] == "pt"):
        google_translate_language = "pt"
    elif(google_translate_language == "zh_Tw"):
        google_translate_language = "zh-tw"
    elif(google_translate_language == "zh"):
        google_translate_language = "zh-cn"
    

    subprocess.run(["cd", "tldr", "&&", "git", "pull"], shell=True)
    pages_folder = f"tldr/pages/{folder}"
    pages_lang_folder = f"tldr/pages.{language}/{folder}"

    if not os.path.exists(pages_lang_folder):
        os.makedirs(pages_lang_folder)

    pages_files = os.listdir(pages_folder)
    pages_lang_files = os.listdir(pages_lang_folder)
    
    translator = Translator()

    for file in pages_files:
        if file not in pages_lang_files:
            embed = discord.Embed(
            title="Translating Pages",
            description="We will send you the first not translated file in your selected language and folder. We will send you this line-by-line. You have to send us back every line translated into selected lang.",
            color=discord.Colour.blurple(),
            )
            embed.add_field(name="Selected File:", value=file)
            embed.add_field(name="Selected Lang:", value=f"{language}", inline=True)
            embed.set_footer(text="created by spageektti", icon_url="https://github.com/spageektti.png")
            embed.set_author(name="TLDR Translations", icon_url="https://github.com/tldr-pages.png")

            await ctx.send("", embed=embed)
            with open(os.path.join(pages_folder, file), 'r') as f:
                content = f.readlines()

            line_count = -1
            for line in content:
                if(line != "\n"):
                    line_count += 1

            translated_content = []
            started = False
            current_line = 0
            if not test:
                for line in content:
                    if(line != "\n" and started):
                        current_line += 1
                        await ctx.send(f"> Line {current_line} of {line_count}")
                        await ctx.send(f"```md\n{line}```")
                        try:
                            await ctx.send(translator.translate(line, dest=google_translate_language).text)
                        except x:
                            await ctx.send("An error occurred. The automated translation will not be displayed.")
                        translated_line = await bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel.type == discord.ChannelType.private)
                        if(translated_line.content == "."):
                            translated_content.append(line)
                        else:
                            translated_content.append(translated_line.content + "\n")
                    else:
                        translated_content.append(line)
                        started = True
            
            result = ""
            for line in translated_content:
                result += line
            
            await ctx.send('```md\n' + result + '```')
            print(result)

            embed.title = "You have successfully translated the file."
            embed.description = "Now you should upload this translation to GitHub and open a pull request.\nWould you like me to send you step-by-step instructions?\n(answer with `yes`/`no`)"
            embed.color = discord.Colour.green()
            await ctx.send(embed=embed)

            response = await bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel.type == discord.ChannelType.private)
            if(response.content == "yes"):
                for i in range(1, 7):
                    file_path = f"assets/{i}.gif"
                    if os.path.exists(file_path):
                        await ctx.send(guide[i], file=discord.File(file_path))
                    else:
                        await ctx.send(guide[i])
            else:
                await ctx.send("OK.")
            break
    

bot.run(os.getenv('DISCORD_TOKEN'))