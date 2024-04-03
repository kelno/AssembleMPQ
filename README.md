# Assemble MPQ

Simple CLI tool to create an MPQ file from of a directory.  


https://github.com/kelno/AssembleMPQ/assets/3866946/df89bddb-615d-4f81-860c-62eb7ea3ccbb


https://github.com/kelno/AssembleMPQ/assets/3866946/8e72dd16-da5c-4f55-b9f1-7410feeddfdd


Quick and dirty fork from https://github.com/ladislav-zezula/StormLib/  


## How to use
### Building  

You can either use the provided StormLib.sln (recommanded), or build with CMake.  
Build in release, get the built Assemble.exe in `\bin\Assemble\x64\Release`

### Usage

```bash
Usage: Assemble.exe [--nolistfile] directory_path [mpq_file_name]
Arguments:
  --nolistfile       : (Optional) Prevent generating listfile
  --help             : (Optional) Print this help text
  directory_path     : Path to the directory
  mpq_file_name      : (Optional) Name of the MPQ file (default: Patch-X.MPQ)
```
