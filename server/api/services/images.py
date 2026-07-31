"""Teacher photo processing: uploads in, one small square JPEG out.

The browser hands us a ``data:`` URL of arbitrary format and size (a 4 MB PNG
straight from a phone camera is normal). Storing that verbatim bloats both the
SQLite file and every ``GET /teachers`` response, since photos ride along with
the teacher list.

:func:`encode_photo` therefore normalises an upload once, on write: EXIF
orientation is applied, the image is cropped to a centred square, downscaled to
at most :data:`PHOTO_SIZE` and re-encoded as JPEG. Only the bare base64 payload
is persisted — the ``data:`` prefix is re-attached by :func:`to_data_url` when
the frontend asks for it, which keeps the stored column free of a redundant,
format-specific header.
"""

from __future__ import annotations

import base64
import binascii
from io import BytesIO
from typing import Final

from PIL import Image, ImageOps, UnidentifiedImageError

PHOTO_SIZE: Final[int] = 256
"""Side of the stored square, in pixels. Avatars render at ≤ 64 CSS px."""

JPEG_QUALITY: Final[int] = 82
"""Quality/size trade-off; visually lossless at avatar scale (~12 KB)."""

MAX_UPLOAD_BYTES: Final[int] = 12 * 1024 * 1024
"""Largest accepted decoded upload. Bigger files are rejected, not resized."""

DATA_URL_PREFIX: Final[str] = "data:image/jpeg;base64,"

_JPEG_BACKGROUND: Final[tuple[int, int, int]] = (255, 255, 255)


class PhotoError(Exception):
    """An uploaded photo could not be decoded or re-encoded."""


class PhotoTooLargeError(PhotoError):
    """The uploaded payload exceeds :data:`MAX_UPLOAD_BYTES`."""


def encode_photo(source: str) -> str:
    """Normalise an uploaded image to the stored base64 JPEG payload.

    Args:
        source: Either a ``data:`` URL (as produced by the browser's
            ``FileReader.readAsDataURL``) or a bare base64 string.

    Returns:
        Base64-encoded JPEG bytes, without any ``data:`` prefix.

    Raises:
        PhotoTooLargeError: The upload is larger than :data:`MAX_UPLOAD_BYTES`.
        PhotoError: The payload is not valid base64 or not a readable image.
    """
    return base64.b64encode(_to_square_jpeg(_decode(source))).decode("ascii")


def to_data_url(photo: str | None) -> str | None:
    """Re-attach the ``data:`` prefix so a browser can render the photo as-is.

    Args:
        photo: A stored base64 JPEG payload, or ``None`` for "no photo".

    Returns:
        A renderable ``data:`` URL, or ``None`` when there is no photo.
    """
    if not photo:
        return None
    # Rows written before photos were normalised still hold a full data URL;
    # they render fine as they are and get compressed on the next upload.
    if photo.startswith("data:"):
        return photo
    return DATA_URL_PREFIX + photo


def _decode(source: str) -> bytes:
    """Strip an optional ``data:`` header and base64-decode the payload."""
    payload = source.split(",", 1)[-1] if source.startswith("data:") else source
    payload = "".join(payload.split())  # tolerate wrapped/padded base64
    if not payload:
        raise PhotoError("empty photo payload")
    # 4 base64 chars encode 3 bytes: reject oversized uploads before decoding.
    if len(payload) // 4 * 3 > MAX_UPLOAD_BYTES:
        raise PhotoTooLargeError(f"photo exceeds {MAX_UPLOAD_BYTES} bytes")
    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as err:
        raise PhotoError("photo payload is not valid base64") from err


def _to_square_jpeg(raw: bytes) -> bytes:
    """Centre-crop to a square, downscale and encode as JPEG."""
    try:
        with Image.open(BytesIO(raw)) as image:
            image.load()
            # Phone cameras store landscape pixels plus an orientation tag.
            oriented = ImageOps.exif_transpose(image) or image
            side = min(PHOTO_SIZE, *oriented.size)  # never upscale a small photo
            square = ImageOps.fit(
                _flatten(oriented),
                (side, side),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            buffer = BytesIO()
            square.save(
                buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True,
            )
            return buffer.getvalue()
    except (UnidentifiedImageError, OSError, ValueError) as err:
        raise PhotoError("image could not be processed") from err


def _flatten(image: Image.Image) -> Image.Image:
    """Composite any transparency onto white — JPEG has no alpha channel."""
    if image.mode == "RGB":
        return image
    rgba = image.convert("RGBA")
    canvas = Image.new("RGB", rgba.size, _JPEG_BACKGROUND)
    canvas.paste(rgba, mask=rgba.getchannel("A"))
    return canvas
