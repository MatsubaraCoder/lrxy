from typing import Union, Generator
from pathlib import Path

from lrxy.formats import Flac, Mp3, Mp4
from lrxy.utils import LRCLibAPI
from lrxy.base_files import BaseFile
from lrxy.formats import SUPPORTED_FORMATS
from lrxy.exceptions import (
    LrxyException, PathNotExistsError, FileError, UnsupportedFileFormatError)


def iter_files(*file_paths: Union[Path, str]) -> Generator[dict, None, None]:
    for file_path in file_paths:
        file = BaseFile(file_path)

        try:
            if not file._check_path_exists():
                raise PathNotExistsError(str(file.path))

            if not file._check_is_file():
                raise FileError(str(file.path))

            match file.extension:
                case ".mp3":
                    file = Mp3(file.path)
                case ".flac":
                    file = Flac(file.path)
                case ".mp4":
                    file = Mp4(file.path)
                case _:
                    raise UnsupportedFileFormatError(
                        file.extension, SUPPORTED_FORMATS
                    )

        except LrxyException as e:
            yield {file.path: f"Error: {e}"}

        else:
            lrc = LRCLibAPI(file.get_tags())

            if lrc["success"]:
                plain_lyric = lrc["data"].get("plainLyrics")
                synced_lyric = lrc["data"].get("syncedLyrics")
                lyric = synced_lyric or plain_lyric
                if lyric:
                    file.embed_lyric(lyric)
                    yield {file.path: "success"}
                else:
                    yield {file.path: "unsuccessful"}
            else:
                yield {file.path: "unsuccessful"}
