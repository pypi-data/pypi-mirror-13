#!/usr/bin/env python
# -*- coding: utf-8 -*-
("""
Usage:
  img2txt.py <imgfile> [--maxLen=<n>] [--fontSize=<n>] [--color] [--ansi]"""
    """[--bgcolor=<#RRGGBB>] [--antialias]
  img2txt.py (-h | --help)

Options:
  -h --help             show this screen.
  --ansi                output an ANSI rendering of the image
  --color               output a colored HTML rendering of the image.
  --antialias           causes any resizing of the image to use antialiasing
  --fontSize=<n>        sets font size (in pixels) when outputting HTML,
                        default: 7
  --maxLen=<n>          resize image so that larger of width or height matches
                        maxLen, default: 100px
  --bgcolor=<#RRGGBB>   if specified, is blended with transparent pixels to
                        produce the output. In ansi case, if no bgcolor set, a
                        fully transparent pixel is not drawn at all, partially
                        transparent pixels drawn as if opaque
""")

import sys
from docopt import docopt
from PIL import Image


def HTMLColorToRGB(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#':
        colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError(
            "input #{0} is not in #RRGGBB format".format(colorstring))
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)


def alpha_blend(src, dst):
    # Does not assume that dst is fully opaque
    # See https://en.wikipedia.org/wiki/Alpha_compositing - section on "Alpha
    # Blending"
    src_multiplier = (src[3] / 255.0)
    dst_multiplier = (dst[3] / 255.0) * (1 - src_multiplier)
    result_alpha = src_multiplier + dst_multiplier
    if result_alpha == 0:       # special case to prevent div by zero below
        return (0, 0, 0, 0)
    else:
        return (
            int(((src[0] * src_multiplier) +
                (dst[0] * dst_multiplier)) / result_alpha),
            int(((src[1] * src_multiplier) +
                (dst[1] * dst_multiplier)) / result_alpha),
            int(((src[2] * src_multiplier) +
                (dst[2] * dst_multiplier)) / result_alpha),
            int(result_alpha * 255)
        )


def getANSIcolor_for_rgb(rgb):
    # Convert to web-safe color since that's what terminals can handle in
    # "256 color mode"
    #   https://en.wikipedia.org/wiki/ANSI_escape_code
    # http://misc.flogisoft.com/bash/tip_colors_and_formatting#bash_tipscolors_and_formatting_ansivt100_control_sequences # noqa
    # http://superuser.com/questions/270214/how-can-i-change-the-colors-of-my-xterm-using-ansi-escape-sequences # noqa
    websafe_r = int(round((rgb[0] / 255.0) * 5))
    websafe_g = int(round((rgb[1] / 255.0) * 5))
    websafe_b = int(round((rgb[2] / 255.0) * 5))

    # Return ANSI coolor
    # https://en.wikipedia.org/wiki/ANSI_escape_code (see 256 color mode
    # section)
    return int(((websafe_r * 36) + (websafe_g * 6) + websafe_b) + 16)


def getANSIfgarray_for_ANSIcolor(ANSIcolor):
    """Return array of color codes to be used in composing an SGR escape
    sequence. Using array form lets us compose multiple color updates without
    putting out additional escapes"""
    # We are using "256 color mode" which is available in xterm but not
    # necessarily all terminals
    # To set FG in 256 color you use a code like ESC[38;5;###m
    return ['38', '5', str(ANSIcolor)]


def getANSIbgarray_for_ANSIcolor(ANSIcolor):
    """Return array of color codes to be used in composing an SGR escape
    sequence. Using array form lets us compose multiple color updates without
    putting out additional escapes"""
    # We are using "256 color mode" which is available in xterm but not
    # necessarily all terminals
    # To set BG in 256 color you use a code like ESC[48;5;###m
    return ['48', '5', str(ANSIcolor)]


def getANSIbgstring_for_ANSIcolor(ANSIcolor):
    # Get the array of color code info, prefix it with ESCAPE code and
    # terminate it with "m"
    return "\x1b[" + ";".join(getANSIbgarray_for_ANSIcolor(ANSIcolor)) + "m"


def generate_ANSI_to_set_fg_bg_colors(cur_fg_color, cur_bg_color, new_fg_color,
                                      new_bg_color):
    # This code assumes that ESC[49m and ESC[39m work for resetting bg and fg
    # This may not work on all terminals in which case we would have to use
    # ESC[0m
    # to reset both at once, and then put back fg or bg that we actually want

    # We don't change colors that are already the way we want them - saves
    # lots of file size

    # use array mechanism to avoid multiple escape sequences if we need to
    # change fg and bg
    color_array = []

    if new_bg_color != cur_bg_color:
        if new_bg_color is None:
            color_array.append('49')        # reset to default
        else:
            color_array += getANSIbgarray_for_ANSIcolor(new_bg_color)

    if new_fg_color != cur_fg_color:
        if new_fg_color is None:
            color_array.append('39')        # reset to default
        else:
            color_array += getANSIfgarray_for_ANSIcolor(new_fg_color)

    if len(color_array) > 0:
        return "\x1b[" + ";".join(color_array) + "m"
    else:
        return ""


def generate_ANSI_from_pixels(pixels, width, height, bgcolor_rgba,
                              get_pixel_func=None, is_overdraw=False):
    """Does not output final newline or reset to particular colors at end --
    caller should do that if desired bgcolor_rgba=None is treated as default
    background color."""
    if get_pixel_func is None:
        # just treat pixels as 2D array
        get_pixel_func = lambda pixels, x, y: (" ", pixels[x, y])

    # Compute ANSI bg color and strings we'll use to reset colors when moving
    # to next line
    if bgcolor_rgba is not None:
        bgcolor_ANSI = getANSIcolor_for_rgb(bgcolor_rgba)
        # Reset cur bg color to bgcolor because \n will fill the new line with
        # this color
        bgcolor_ANSI_string = getANSIbgstring_for_ANSIcolor(bgcolor_ANSI)
    else:
        bgcolor_ANSI = None
        # Reset cur bg color default because \n will fill the new line with
        # this color
        # reset bg to default (if we want to support terminals that can't
        # handle this will need to instead use 0m which clears fg too and then
        # when using this reset prior_fg_color to None too
        bgcolor_ANSI_string = "\x1b[49m"

    # removes all attributes (formatting and colors) to start in a known state
    string = "\x1b[0m"

    prior_fg_color = None       # this is an ANSI color not rgba
    prior_bg_color = None       # this is an ANSI color not rgba
    cursor_x = 0

    for h in range(height):
        for w in range(width):

            draw_char, rgba = get_pixel_func(pixels, w, h)

            # Handle fully or partially transparent pixels - but not if it is
            # the special "erase" character (None)
            skip_pixel = False
            if draw_char is not None:
                alpha = rgba[3]
                if alpha == 0:
                    skip_pixel = True       # skip any full transparent pixel
                elif alpha != 255 and bgcolor_rgba is not None:
                    # non-opaque so blend with specified bgcolor
                    rgba = alpha_blend(rgba, bgcolor_rgba)

            if not skip_pixel:
                this_pixel_str = ""
                # Throw away alpha channel - can still have non-fully-opaque
                # alpha value here if bgcolor was partially transparent or if
                # no bgcolor and not fully transparent. Could make argument to
                # use threshold to decide if throw away (e.g. >50% transparent)
                # vs. consider opaque (e.g. <50% transparent) but at least for
                # now we just throw it away
                rgb = rgba[:3]
                # If we've got the special "erase" character turn it into
                # outputting a space using the bgcolor which if None will
                # just be a reset to default bg which is what we want
                if draw_char is None:
                    draw_char = " "
                    color = bgcolor_ANSI
                else:
                    # Convert from RGB to ansi color, using closest color
                    color = getANSIcolor_for_rgb(rgb)
                    # Optimization - if we're drawing a space and the color is
                    # the same as a specified bg color then just skip this. We
                    # need to make this check here because the conversion to
                    # ANSI can cause colors that didn't match to now match
                    # We cannot do this optimization in overdraw mode because
                    # we cannot assume that the bg color is already drawn at
                    # this location
                    if not is_overdraw and (draw_char == " ") and \
                            (color == bgcolor_ANSI):
                        skip_pixel = True

                if not skip_pixel:

                    if len(draw_char) > 1:
                        raise ValueError(
                            "Not allowing multicharacter draw strings")

                    # If we are not at the cursor x location (happens if we
                    # skip pixels) output sequence to get there
                    # This is how we implement transparency - we don't draw
                    # spaces, we skip via cursor moves
                    if cursor_x < w:
                        # **SIZE - Note that when the bgcolor is specified
                        # (not None) and not overdrawing another drawing
                        # (as in an animation case) an optimization could be
                        # performed to draw spaces rather than output cursor
                        # advances. This would use less
                        # size when advancing less than 3 columns since the min
                        # escape sequence here is len 4. Not implementing this
                        # now
                        # code to advance N columns ahead
                        string += "\x1b[{0}C".format(w - cursor_x)
                        cursor_x = w

                    # Generate the ANSI sequences to set the colors the way we
                    # want them
                    if draw_char == " ":

                        # **SIZE - If we are willing to assume terminals that
                        # support ECH (Erase Character) as specified in here
                        # http://vt100.net/docs/vt220-rm/chapter4.html we could
                        # replace long runs of same-color spaces with single
                        # ECH codes. Seems like it is only correct to do this
                        # if BCE is supported though (
                        # http://superuser.com/questions/249898/how-can-i-prevent-os-x-terminal-app-from-overriding-vim-colours-on-a-remote-syst) # noqa
                        # else "erase" would draw the _default_ background
                        # color not the currently set background color

                        # We are supposed to output a space, so we're going to
                        # need to change the background color. No, we can't
                        # output an "upper ascii" character that fills the
                        # entire foreground - terminals don't display these the
                        # same way, if at all.
                        # Since we're outputting a space we can leave the prior
                        # fg color intact as it won't be used
                        string += generate_ANSI_to_set_fg_bg_colors(
                            prior_fg_color, prior_bg_color, prior_fg_color,
                            color)
                        prior_bg_color = color

                    else:
                        # We're supposed to output a non-space character, so
                        # we're going to need to change the foreground color
                        # and make sure the bg is set appropriately
                        string += generate_ANSI_to_set_fg_bg_colors(
                            prior_fg_color, prior_bg_color, color,
                            bgcolor_ANSI)
                        prior_fg_color = color
                        prior_bg_color = bgcolor_ANSI

                    # Actually output the character
                    string += draw_char

                    cursor_x = cursor_x + 1

        # Handle end of line - unless last line which is NOP because we don't
        # want to do anything to the _line after_ our drawing
        if (h + 1) != height:

            # Reset bg color so \n fills with it
            string += bgcolor_ANSI_string
            prior_bg_color = bgcolor_ANSI       # because it has been reset

            # Move to next line. If this establishes a new line in the terminal
            # then it fills the _newly established line_
            # to EOL with current bg color. However, if cursor had been moved
            # up and this just goes back down to an existing
            # line, no filling occurs
            string += "\n"
            cursor_x = 0

    return string


def load_and_resize_image(imgname, antialias, maxLen):

    img = Image.open(imgname)

    # force image to RGBA - deals with palettized images (e.g. gif) etc.
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # resize up or down so that longer side of image is maxLen
    if maxLen is not None:
        native_width, native_height = img.size
        rate = float(maxLen) / max(native_width, native_height)
        width = int(rate * native_width) * 2
        height = int(rate * native_height)

        if native_width != width or native_height != height:
            img = img.resize((width, height), Image.ANTIALIAS
                             if antialias else Image.NEAREST)

    return img


def foo():

    maxLen = 30.0

    try:
        antialias = True
        imgname = 'avatar2.png'
        img = load_and_resize_image(imgname, antialias, maxLen)
    except IOError:
        exit("File not found: " + imgname)

    # get pixels
    pixel = img.load()
    width, height = img.size
    # reset bg to default (if we want to support terminals that can't
    # handle this will need to instead use 0m which clears fg too and
    # then when using this reset prior_fg_color to None too
    fill_string = "\x1b[49m"
    fill_string += "\x1b[K"          # does not move the cursor
    sys.stdout.write(fill_string)

    sys.stdout.write(
        generate_ANSI_from_pixels(pixel, width, height, None))

    # Undo residual color changes, output newline because
    # generate_ANSI_from_pixels does not do so
    # removes all attributes (formatting and colors)
    sys.stdout.write("\x1b[0m\n")

    sys.stdout.flush()
