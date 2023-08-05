##########################################################
raaSAFT - coarse grained SAFT-gamma Mie molecular dynamics
##########################################################

- raaSAFT (pronounced "raw saft") is a Python framework that makes it easy to set up coarse-grained molecular dynamics simulations.
- raaSAFT runs with HOOMD-blue as a backend, so you can use GPU power. Initial support for using GROMACS has been added.
- raaSAFT uses the SAFT-gamma Mie force field, a powerful coarse-graining method
  that gives accuracy comparable to atomistic models, with runtimes that are
  orders of magnitude shorter.
- Raasaft is a Norwegian word meaning "pure fruit syrup". Apart from the obvious saft <-> SAFT pun, "raa" means crude/raw/coarse, so it is twice as punny.

Installation
============

**Dependencies:**

- raaSAFT uses HOOMD-blue, see the `HOOMD-blue install guide <https://codeblue.umich.edu/hoomd-blue/doc/page_install_guide.html>`_.
- For now this is a dependency even if you want to run with GROMACS. The non-GPU version of HOOMD-blue is sufficient.
- Note that HOOMD-blue runs on Linux or Mac OSX. Windows is not supported.

**Simple installation:**

.. code-block:: bash

   pip install raasaft

   # or to upgrade
   pip install --upgrade raasaft

   # To start using raaSAFT:
   mkdir raasaft && cd raasaft
   raasaft_init
   # You now have the helpful directories tutorials/ replication/ and mysaft/
   ls

   # Read the "Running simulations" section below.

**Installation for advanced users / contributors:**

- Install dependencies. This includes HOOMD-blue and the Python packages `future` and `requests`.
- Clone the repo at http://bitbucket.org/asmunder/raasaft
    - The `maint` branch should be as stable as the version on PyPi
    - The `master` branch changes frequently and may not always be stable
- You probably want to add the repo directory to your PYTHONPATH.

Running simulations with raaSAFT
================================

- Look at the README.txt file in `raasaft/tutorials/` for examples of how to use raaSAFT. 
- In `raasaft/replication/` we include setups that can be used to replicate the findings of various papers.
- In `raasaft/mysaft/` you find an example of how to add your own models for new molecules.
    - You can use these user-defined models with e.g.  

.. code-block:: python

      from mysaft.example import Example
      ex = Example(count=1e3)

- If you want to use these models in jobscripts in different directories, add the full path to the `raasaft` folder to your `PYTHONPATH` shell variable (put this in your `.bashrc` file to make it permanent), e.g.:  
      `export PYTHONPATH=$PYTHONPATH:"/path/to/raasaft"`
- Contributions to raaSAFT with new models are always welcome, assuming the model has seen at least some level of validation.

Bottled SAFT
============

You can get models (force field parameters) for 6000+ molecules from our database called Bottled SAFT: 

http://www.bottledsaft.org 

This web application provides scripts that implement the search result in raaSAFT for you!

License
=======

The code is Free and Open Source software under the MIT license.

Contribute
==========

All contributions are welcome!

Contact
=======

Email Aasmund at aaervik@gmail.com



