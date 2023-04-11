from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import typing
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from mako.template import Template
import magic
from wand.image import Image
import wand.exceptions
import tempfile

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def image_convert(input_file: UploadFile,
                  width=None,
                  height=None,
                  target_type=None) -> tempfile.SpooledTemporaryFile:
    with Image(file=input_file.file) as image:
        tmp_file = tempfile.SpooledTemporaryFile()

        if width is None:
            width = image.width

        if height is None:
            height = image.height

        image.scale(columns=width, rows=height)

        # Raises ValueError if type is unsupported
        if target_type:
            with image.convert(target_type) as converted:
                converted.save(file=tmp_file)
                return tmp_file

        image.save(file=tmp_file)
        return tmp_file


IMAGE_TARGET_TEMPLATES = {
    "formats": {
        "image/jpeg": {
            "format_name": "JPEG Image",
            "processor": "imagemagick",
            "internal_type": "jpeg",
            "extension": "jpg"
        },
        "image/vnd.microsoft.icon": {
            "format_name": "Icon",
            "processor": "imagemagick",
            "extension": "ico"
        }
    }
}


@app.get("/")
def index():
    return RedirectResponse(url="/static/pages/image.html")


def iterfile(fileobj):
    with fileobj as file:
        yield from file


@app.post("/api/process-image")
def file_upload(fileobj: typing.Annotated[UploadFile, File()],
                target_type: typing.Annotated[str, Form()],
                width: typing.Annotated[int, Form()] = None,
                height: typing.Annotated[int, Form()] = None):
    if not fileobj.filename:
        raise HTTPException(status_code=400, detail="Empty file in request")
    if target_type not in IMAGE_TARGET_TEMPLATES["formats"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target_type: {target_type}")

    ext = IMAGE_TARGET_TEMPLATES["formats"][target_type]["extension"]
    try:
        tmpfile = image_convert(fileobj,
                                target_type=IMAGE_TARGET_TEMPLATES["formats"].get(target_type).get("internal_type"),
                                width=width,
                                height=height)
    except wand.exceptions.MissingDelegateError:
        raise HTTPException(
            status_code=400,
            detail="Missing converter for input file")
    tmpfile.seek(0)
    without_ext = ".".join(fileobj.filename.split(".")[:-1])
    disposition = f'filename="{without_ext}_converted.{ext}"'
    return Response(
        content=tmpfile.read(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; {disposition}'})
