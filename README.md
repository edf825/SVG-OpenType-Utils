SVG in OpenType Utils
=====================

What Is This?
-------------

This is a collection of (well, two; only one of which is relevant anymore) tools for creating SVG in Opentype
fonts. [1]

Simply put, SVG in Opentype is a way of defining glyphs for Opentype fonts by embedding SVG documents inside
those fonts.

This feature is currently supported by Firefox only. OpenType glyph definitions are still kept though, so you
can use the resulting fonts anywhere.

Trying It Out
-------------

To try this out in Firefox, you'll have to turn on the `gfx.font_rendering.opentype_svg.enabled` preference.
(navigate to about:config, search for `svg`, and double click on the preference with that name)

Then point Firefox at http://flores.geek.nz/t/svgot

Making a Font
-------------

You can use the `insertsvg/insertsvg.py` script to create an SVG font of your own. I've already provided a font
and SVG documents so you can try it for yourself.

In the `insertsvg` directory, try:

`./insertsvg.py LiberationSerif-Regular.ttf out.ttf reftest?.svg`

This will spit out a file named `out.ttf` with the glyph definitions from `reftest1.svg`.

You can then include this `out.ttf` in a web site like any other web font.

Check out the `reftest?.svg` files to get an idea of how these SVG glyph definitions work. For a more detailed
explanation of things, check out the spec linked below.

Making a Rubbish Font
---------------------

`insertsvg/insertrubbish.py` is a script for inserting arbitrary data into the
'SVG ' Opentype table. As the name suggests, I use it for inserting rubbish into
the table to see if my implementation can safely ignore it.

More Information
----------------

For more information on the SVG in Opentype format itself, the (draft) specification is very readable and can be found
at http://dev.w3.org/SVG/modules/fonts/SVG-OpenType.html

[1] A better name for this feature TBD
