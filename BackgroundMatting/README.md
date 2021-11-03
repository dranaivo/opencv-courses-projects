# Background Matting

Use this script to do [**chroma keying**](https://en.wikipedia.org/wiki/Chroma_key) : the background of a video, with uniform color, is replaced with another background. Usually, the background is colored green, but you can have other colors.

**Pre-requesites :** You should have a video with green (or any other color) background, as well as the picture of the background ( `background.jpeg` ).

## Usage

You will find the usage instructions in the module docstring.

![background_matting](background_matting.gif)

## Principle

To achieve the chroma keying, the main task is to compute a binary mask representing the background. 

The selected green patch is used as a reference, which is converted to the `HSV` format (better suited for color processing).
The mean `hue` value of this patch is then computed. 

Finally, the **tolerance** controls how far away from this mean value $\mu$ the background `hue` should be : all pixel $i$ whose `hue` satisfies the condition $\mid h(i) - \mu \mid < tolerance$ is part of the background.