#!/usr/bin/env python3
import sys

sys.path.append("/usr/local/opt/fontforge/lib/python3.7/site-packages")

import fontforge

f = fontforge.open("/usr/local/opt/sfmono-square/share/fonts/SFMonoSquare-Regular.otf")
print(f"name: {f.familyname}")
print(f"version: {f.version}")
