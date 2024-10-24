# 外部モジュール
import asyncio
import discord
from discord.ext import commands
import io
import os
import pdf2image

# 内部モジュール
from .mylib.PDFConverter import PDFConverter


class FileViewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supported_extensions = [
            # .pdf
            "application/pdf",
            # .xls
            "application/vnd.ms-excel",
            # .xlsx
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            # .doc
            "application/msword",
            # .docs
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            # .ppt
            "application/vnd.ms-powerpoint",
            # .pptx
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.attachments) == 0:
            return
        if message.channel.type != discord.ChannelType.text:
            return
        # 添付されたファイルの中に対応している拡張子がなければ無視
        attachments = [
            attachment
            for attachment in message.attachments
            if attachment.content_type in self.supported_extensions
        ]
        if len(attachments) == 0:
            return
        thread = await message.create_thread(name=attachments[0].filename)
        for attachment in attachments:
            loop = asyncio.get_running_loop()
            images = []
            # pdf -> jpeg
            if attachment.content_type == "application/pdf":
                pdf_io = io.BytesIO()
                await attachment.save(pdf_io)
                images = await loop.run_in_executor(
                    None, pdf2image.convert_from_bytes, pdf_io.read()
                )
            elif attachment.content_type in self.supported_extensions:
                await attachment.save(attachment.filename)
                converter = PDFConverter(attachment.filename, ".")
                await loop.run_in_executor(None, converter.start)
                images = await loop.run_in_executor(
                    None,
                    pdf2image.convert_from_path,
                    attachment.filename.replace(attachment.filename.split(".")[-1], "pdf"),
                )
                os.remove(attachment.filename)
                os.remove(attachment.filename.replace(attachment.filename.split(".")[-1], "pdf"))

            await thread.send(
                embed=discord.Embed(
                    title=attachment.filename, color=discord.Color.blue()
                )
            )
            # 最大10枚ごとの2次元配列に変換
            images = [images[idx : idx + 10] for idx in range(0, len(images), 10)]
            count = 1
            for image_container in images:
                files = []
                for image in image_container:
                    fileio = io.BytesIO()
                    image.save(fileio, format="jpeg")
                    fileio.seek(0)
                    files.append(discord.File(fileio, filename="image.jpg"))
                    count += 1
                await thread.send(
                    content=f"{count-len(files)}~{count-1}ページ", files=files
                )


async def setup(bot):
    await bot.add_cog(FileViewer(bot))

