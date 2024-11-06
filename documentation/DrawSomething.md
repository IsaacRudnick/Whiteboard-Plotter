# Draw Something

If the system is set up and you just want to have it draw something, follow these steps:

1. Place the SVG file you want to draw in the [user/SVGs/](user/SVGs/) directory.

> Note: The robot will draw the OUTLINE of any SVG shapes, but doesn't care about fill. Two identical-looking SVG files may produce different results. For example, a straight line with a thick stroke will be drawn as a line, even though it looks like a rectangle.

2. In the [user_setup.py](user_setup.py) file, set the `INPUT_IMG_FILE_PATH` variable to the path to your SVG, e.g. `"user/SVGs/your_svg_file.svg"`

3. Run [main.py](main.py) and follow the instructions in the console, which will guide you through the preview and drawing process.
