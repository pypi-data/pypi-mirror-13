# raaSAFT #
![raasaft-wide.jpg](https://bitbucket.org/repo/pn6BAR/images/2465645789-raasaft-wide.jpg)

###### Illustrative image courtesy of [www.frukt.no](frukt.no)

### What is raaSAFT? ###

* raaSAFT (pronounced "raw saft") is a Python framework for easy coarse-grained molecular dynamics simulations.
* raaSAFT runs with HOOMD-blue as a backend, so you can use GPU power. Initial support for using GROMACS has been added.
* raaSAFT uses the SAFT-gamma Mie force field, a coarse-graining method which is thermodynamically consistent, and not based on tuning to atomistic simulations
* Raasaft is a Norwegian word meaning "pure fruit syrup". Apart from the obvious saft <-> SAFT pun, "raa" means crude/raw/**coarse**, so it is twice as punny.

### Installing raaSAFT ###

**Dependencies:**

* raaSAFT uses HOOMD-blue, see the [HOOMD-blue install guide](https://codeblue.umich.edu/hoomd-blue/doc/page_install_guide.html).
    * For now this is a dependency even if you want to run with GROMACS. The non-GPU version of HOOMD-blue is sufficient.
* Note that HOOMD-blue runs on Linux or Mac OSX. Windows is not supported.

**Simple installation:**

* System-wide install: `sudo pip install raasaft`
* Local installation: `pip install --user raasaft`
 
* To upgrade: add `--upgrade` after `install`

* To start using raaSAFT: make a new folder, enter it and run the command  
  `raasaft_init`  
  to add the helpful directories `tutorials/`, `replication/` and `mysaft/`.
* Read the "Running simulations" section below.

**Installation for advanced users / contributors:**

* Install dependencies. This includes HOOMD-blue and the Python packages `future` and `requests`.
* Clone this repo
    * The `maint` branch should be as stable as the version on PyPi
    * The `master` branch changes frequently and may not always be stable
* The `raasaft_init` command will not be in your path unless you put it there.

### Running simulations with raaSAFT ###
* Make sure you have run the `raasaft_init` command in the folder where you want to run your simulations.
    * Let's call this folder "trysaft".
* Look at the README.txt file in "trysaft/tutorials/" for examples of how to use raaSAFT. 
* In "trysaft/replication/" we include setups that can be used to replicate the findings of various papers.
* In "trysaft/mysaft/" you find an example of how to add your own models for new molecules.
    * You can use these user-defined models with e.g.  
      `from mysaft.example import Example`  
      `ex = Example(count=1e3)`
    * If you want to use these models in jobscripts in different directories, add the full path to the "trysaft" folder to your `PYTHONPATH` shell variable, e.g.:  
      `export PYTHONPATH=$PYTHONPATH:"$HOME/trysaft"`
    * Contributions to raaSAFT with new models are always welcome, assuming the model has seen at least some level of validation.

### Bottled SAFT ###
You can get models (force field parameters) for 6000+ molecules from our database called Bottled SAFT: [www.bottledsaft.org](http://www.bottledsaft.org).  
This web application provides scripts that implement the search result in raaSAFT for you!
 
### License ###
* The code is Free and Open Source software under the [MIT license](https://bitbucket.org/asmunder/raasaft/src/master/LICENSE.txt).

### Contribute ###
* All contributions are welcome!

### Contact ###
* Email Åsmund at aaervik@gmail.com