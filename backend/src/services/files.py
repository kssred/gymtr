from pathlib import Path

import aiofiles
from fastapi import UploadFile

from src.utils.shortcuts import get_unique_filename


async def write_file(path: Path, file: UploadFile) -> Path:
    """Записать файл в ОС"""

    if path.exists():
        new_filename = get_unique_filename(path.name)
        path = path.with_name(new_filename)

    content = await file.read()
    async with aiofiles.open(file=path, mode="wb") as f:
        await f.write(content)

    return path
