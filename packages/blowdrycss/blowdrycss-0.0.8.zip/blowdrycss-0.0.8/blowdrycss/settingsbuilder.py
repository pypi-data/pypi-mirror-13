"""
Declares string for building blowdrycss - settings.py.

**Important:** Only called during initial installation.

"""

# python 2
from __future__ import print_function

__author__ = 'chad nelson'
__project__ = 'blowdrycss'

blowdrycss_settings_dot_py = """\"\"\"
**Parameters:**

| markdown_directory (*string*) -- Generally used for development purposes only.

| project_directory (*string) -- Path to your project directory

| css_directory (*string*) -- Path to your projects CSS directory

| docs_directory (*string*) -- Path to Sphinx docs.

| file_types = (*tuple of strings*) -- All file types/extensions to search for in the defined project_directory
  that contain encoded class selectors.

| timing_enabled (*bool*) -- Run performance timer

| markdown_docs (*bool*) -- Generate a markdown files that provides a quick syntax and clashing alias reference.

| html_docs (*bool*) -- Generate a html file that provides a quick syntax and clashing alias reference.

| rst_docs (*bool*) -- Generate a sphinx rst file that provides a quick syntax and clashing alias reference.

| human_readable (*bool*) -- Generate a standard human readable css file.

| minify (*bool*) -- Generate a minified version of the css file.

| media_queries_enabled (*bool*) -- Generate breakpoint and scaling media queries.

| use_em (*bool*) -- A ``pixels`` to ``em`` unit conversion flag. True enables unit conversion.
  False disables unit conversions meaning any pixel value remains unchanged.

| base (*int*) -- Base used for unit conversion (typically set to 16). The pixel value will be divided by
  ``base`` during unit conversion.

| xxsmall (*tuple of floats*) -- (0px, upper limit in pixels)

| xsmall (*tuple of floats*) -- (xxsmall upper limit + 1px, upper limit in pixels)

| small (*tuple of floats*) -- (xsmall upper limit + 1px, upper limit in pixels)

| medium (*tuple of floats*) -- (small upper limit + 1px, upper limit in pixels)

| large (*tuple of floats*) -- (medium upper limit + 1px, upper limit in pixels)

| xlarge (*tuple of floats*) -- (large upper limit + 1px, upper limit in pixels)

| xxlarge (*tuple of floats*) -- (xlarge upper limit + 1px, upper limit in pixels)

| giant (*tuple of floats*) -- (xxlarge upper limit + 1px, upper limit in pixels)

| xgiant (*tuple of floats*) -- (giant upper limit + 1px, upper limit in pixels)

| xxgiant (*tuple of floats*) -- (xgiant upper limit + 1px, 1E+6) [Technically the upper limit is infinity,
  but CSS does not permit it.]

**cssutils Patch:**

``cssutils`` does not currently support CSS 3 Units.  The patch in this file allows length units of
``q``, ``ch``, ``rem``, ``vw``, ``vh``, ``vmin``, and ``vmax``. It also allows angle units of ``turn``.

\"\"\"

# builtins
from os import getcwd, path
# plugins
from cssutils import profile

__project__ = 'blowdrycss'


# Set project_directory to the one containing the files you want to DRY out.
# Change it to whatever you want.
cwd = getcwd()
markdown_directory = path.join(cwd, 'docs', 'markdown')
project_directory = cwd
css_directory = path.join(cwd, 'css')
docs_directory = path.join(cwd, 'docs')

# All file types/extensions to search for in the defined project_directory that contain encoded class selectors.
# Example format: ('*.html', )
file_types = ('*.html', )

# Boolean Flags
timing_enabled = True           # Run performance timer
markdown_docs = False           # Generate a markdown files that provides a quick syntax and clashing alias reference.
html_docs = False               # Generate a html file that provides a quick syntax and clashing alias reference.
rst_docs = False                # Generate a sphinx rst file that provides a quick syntax and clashing alias reference.
human_readable = True           # Generate a standard human readable css file.
minify = True                   # Generate a minified version of the css file.
media_queries_enabled = True    # Generate breakpoint and scaling media queries.
# ...Not Implemented Yet...
# use_rgb = True
# extra_dry = False             # Combine identical CSS discovered under different class selector names.

# TODO: Implement these in a fashion similar to the performance timer.
# auto_generate = False         # Automatically generates blowdry.css file when a project HTML file is saved.
# http_server = False           # Auto-Start a simple webserver on localhost:8080.
# public_url = False            # Uses ngrok to generate a temporary public url for testings and demo purposes.
# condense_classes = False      # Edits HTML Files after discovering common patterns (Not DRY do not implement).

# Unit Conversion Defaults
use_em = True
base = 16

# Default Screen Breakpoints / Transition Triggers
# Tuple Format (Lower Limit, Upper Limit) in pixels.
# Note: These values change if unit conversion is enabled i.e. ``use_em`` is ``True``.
# Common Screen Resolutions: https://en.wikipedia.org/wiki/List_of_common_resolutions
xxsmall = (px_to_em(0), px_to_em(120))          # 0.0 - 7.5em
xsmall = (px_to_em(121), px_to_em(240))         # 7.5625 - 15.0em
small = (px_to_em(241), px_to_em(480))          # 15.0625 - 30.0em
medium = (px_to_em(481), px_to_em(720))         # 30.0625 - 45.0em  # Typical mobile device break point @ 720px.
large = (px_to_em(721), px_to_em(1024))         # 45.0625 - 64.0em
xlarge = (px_to_em(1025), px_to_em(1366))       # 64.0625 - 85.375em
xxlarge = (px_to_em(1367), px_to_em(1920))      # 85.4375 - 120.0em
giant = (px_to_em(1921), px_to_em(2560))        # 120.0625 - 160.0em
xgiant = (px_to_em(2561), px_to_em(2800))       # 160.0625 - 175.0em
xxgiant = (px_to_em(2801), px_to_em(10**6))     # 175.0625 - float('inf')) # Python 2.x representation of Infinity.

# Patches cssutils
profile._MACROS['length'] = r'0|{num}(em|ex|px|in|cm|mm|pt|pc|q|ch|rem|vw|vh|vmin|vmax)'
profile._MACROS['positivelength'] = r'0|{positivenum}(em|ex|px|in|cm|mm|pt|pc|q|ch|rem|vw|vh|vmin|vmax)'
profile._MACROS['angle'] = r'0|{num}(deg|grad|rad|turn)'
profile._resetProperties()

"""


def write_blowdrycss_settings_dot_py():
    with open('blowdrycss_settings.py', 'wb') as generic_file:
        generic_file.write(bytearray(blowdrycss_settings_dot_py, 'utf-8'))
    print(
        '=' * 42 +
        '\n   "blowdrycss_settings.py" built for blowdrycss.\n\n' +
        '   Open "blowdrycss_settings.py" to customize\n   blowdrycss for your project.\n' +
        '=' * 42
    )