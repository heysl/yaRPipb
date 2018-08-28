# yaRPipb
yet another RaspberryPi photobooth

Yes, I know, places like github are already full of DIY photobooths using a camera and a RaspberryPi.
Here is another one, mainly due to the fact that none of those already available met my idea of a simple photobooth, which basically means just taking pictures and saving them somewhere. No internet connection required, no uploads to some social media site.

Some facts about my setup:

- RaspberryPi B+, but really any model should work, too.
- First model of the RasPi camera module.
- Official RaspberryPi touchscreen, but any monitor should work.
- a big fat red arcade button on top of the case for users to joyfully smash on.
- a simple button inside the case to stop the script without need of a keyboard or any other interface.
- a 64GB USB drive to be safe of crashing SD-cards

Features:

- any parameter I found convenient can be set in a separate config-file, which includes:
  - camera resolution
  - camera iso
  - monitor resolution
  - delay between steps
  - number of pictures
  - file path for results

### Credits

Most inspiration - and actually the whole pygame related part of my code - are from drumminhands photobooth: https://github.com/drumminhands/drumminhands_photobooth


