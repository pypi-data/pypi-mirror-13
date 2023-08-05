BulkReCode (brc)
This copies an entire tree under and recodes the supported formats to specified format (default is ogg) with as many concurrent processes as there are CPU cores on the system

Usage
$ brc -h
usage: brc [-h] [-x] [-t T] [-q Q] [-o O] [-i I] input [output]

Transcode directory trees

positional arguments:
  input       <old directory>
  output      <new directory>

optional arguments:
  -h, --help  show this help message and exit
  -x          Overwrite non-empty output files
  -t T        Transcoding processes
  -q Q        FFmpeg output quality
  -o O        Output format
  -i I        Extra input format
