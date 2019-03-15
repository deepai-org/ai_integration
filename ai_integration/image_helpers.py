from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from PIL import Image
import io


def make_image_rgb_jpeg(img_bytes):
    im = Image.open(io.BytesIO(img_bytes))
    im_rgb = im.convert('RGB')

    with io.BytesIO() as output:
        # Use JPEG to maximize compatibility and tune it to not lose much quality
        im_rgb.save(output, format="JPEG", subsampling=0, quality=99)
        contents = output.getvalue()
        im_rgb.close()
        im.close()
        return contents
