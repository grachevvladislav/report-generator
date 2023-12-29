import io
import pandas as pd


async def downloader(update, context):
    file = await update.message.document.get_file()
    binary_file = await file.download_as_bytearray()
    with io.BytesIO(binary_file) as memory_file:
        print(pd.read_csv(memory_file))



    #await new_file.d
    # #await context.bot.get_file(update.message.document).download()
    # # writing to a custom file
    # with open("file.csv", 'wb') as f:
    #     await context.bot.get_file(update.message.document)
    #     update.message.document.download_to_drive


#
# with io.BytesIO(r.content) as inmemoryfile:
#     mixer.music.init()
#     mixer.music.load(inmemoryfile)
#     mixer.music.play()