## Usage
Install a C++ compiler and Cython as well as other referenced python packages. Just install every package that it complaints missing.
Compile the Cython extension using:
```
python setup.py build_ext --inplace 
```
Run the example using `python dedup.py`.

To run the encode and decode of Elias Gamma, install `rustup` and use `cargo` to build and run.