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

### Sunshine and sunset-animation
Style `sunshine-static` uses ray tracing to render shadows for a fixed sun position. The `sun-azimuth` style argument gives the sun's direction in degrees clockwise from north, while `sun-altitude` gives its angle in degrees above the horizon.

Both sunshine styles accept `subsampling-level`:
- `0` casts one ray from each pixel center (no subsampling)
- `1` casts four offset rays per pixel
- `2` casts four offset rays per pixel, with each ray's position randomly jiggled. Useful to avoid sudden jumps in animations.

Style `sunshine-animation` creates a GIF, each frame being the same as the sunset-static render.

The `sun-azimuth-start` and `sun-altitude-start` arguments specify the starting sun position, while `sun-azimuth-end` and `sun-altitude-end` specify the ending position. `frames` sets the frame count and `duration` sets the total duration in seconds. For example:
```yaml
style: sunset-animation
style-args:
  sun-azimuthstart: 250
  sun-altitudestart: 60
  sun-azimuthend: 270
  sun-altitudeend: 0
  frames: 96
  duration: 4
  subsampling-level: 1
```
Run the usual command to save the animation as `sunset.gif` in the output directory.

Example sunset animation over Montserrat:
![Sunset animation over Montserrat](.readme/montserrat.gif)