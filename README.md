# Elevation data visualizer

## Getting started

Get your environment ready by running:
```sh
make dependencies
```
This will download dependencies and build the binaries.

## How to use
First, download data from https://visors.icgc.cat/appdownloads/. It myst be elevation data in TIF format.

Unzip the download and put it in some directory, for example `data/barcelona` and unzip it.

Create a config file:
```yaml
data-directory: data/barcelona # Where your elevation data is
output-directory: out          # Where the outputs will go to
downsample: 4                  # Ratio to lower resolution. Default 1.
style: shading                 # Style of generated image, see below
style-args:                    # Args for the style, see below
  angle: 180
```

Then run it with: 
```sh
make run
```

## Styles

### Slope
Style `slope` shades terrain based on how inclined it is (i.e. the norm of the gradient).

Here is an example with 2m-resolution data around Barcelona.
![alt text](.readme/slope.png)

Blank areas are outside the source map (in this case it's just the sea).


### Shading
Style `shading` colors the terrain according to the slope in a particular direction. Slopes facing towards this direction will be brighter, and slopes facing against it will be darker.

The direction is expressed as an angle in style-arg `angle`. 0° is north (so shadows go south), 90° is east, and so on until 360° which is north again.

Note: there is no ray-tracing, the image is shaded based exclusively on the direction the ground points towards.

Here is an example with 25cm lidar data around North Barcelona lit from the north west
![alt text](.readme/shading.png)

### Sunshine
Style `sunshine` uses ray tracing with two float style arguments: `sun-azimuth` gives the sun's direction in degrees clockwise from north, while `sun-altitude` gives its angle in degrees above the horizon. Both default to `0.0`.

Style `sunset-animation` renders a looping sunset GIF. The azimuth and altitude specify the starting sun position, and `sun-azimuth-end` and `sun-altitude-end` specify the ending position. `frames` sets the frame count and `duration` sets the total duration in seconds. For example:
```yaml
style: sunset-animation
style-args:
  sun-azimuth: 250
  sun-altitude: 60
  sun-azimuth-end: 270
  sun-altitude-end: 0
  frames: 96
  duration: 4
```
Run the usual command to save the animation as `sunset.gif` in the output directory. GIF frame timing uses hundredths of a second, so the total duration must be a positive multiple of 0.01 seconds and allow at least 0.01 seconds per frame.