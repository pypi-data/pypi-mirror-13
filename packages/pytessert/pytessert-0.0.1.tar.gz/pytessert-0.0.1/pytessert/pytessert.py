"""OCR in Python using the Tesseract engine from Google
https://github.com/baituhuangyu/pytesser
by baituhuangyu
V 0.0.1, 2016/01/01"""

# require tesseract 3.03

import subprocess
import traceback
import StringIO


def image_to_string(tmp_img, language = "eng", psm = "3"):
    """ OCR in Python using the Tesseract """
    try:
        f = StringIO.StringIO()
        tmp_img.save(f, "BMP")
        img = f.getvalue()
        p = subprocess.Popen(["tesseract", "stdin", "stdout", "-l", language, "-psm", psm], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdoutput, erroutput = p.communicate(img)

        # print stdoutput
        return stdoutput
    except Exception, e:
        traceback.print_exc(e)
