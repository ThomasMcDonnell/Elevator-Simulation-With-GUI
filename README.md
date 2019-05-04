# Elevator Simulation
## DIT ASSIGNMENT

### Project Overview

This is an elevator simulation which leverages the Salabim Python Package, developed with a similar take on 
simulation creation as the popular Simpy package.
I choose Salabim over Simpy for two main reasons:
1. Simpy has dropped support for its object oriented api as of Simpy 3
2. Salabim, while supporting the object oriented paradigm, comes with built in with animation through the Pillow python
   package and TKinter. I however, did not have time to implement this part of the library.
   
An Elevator Simulation -
This is an optimisation problem pon implementation you will note that the algorithm or logic for an elevator would 
produce different answers depending on the definition of best outcome. 
The reason for this is that a sequence of locally "optimal" choices don't always yield an optimal solution.

There is no way to tell which "best" will yield the more optimal solution.
You get an answer, but you don't always know weather it is the optimal solution.

Here I chose to focus on the length of stay or wait time that each person waited on there floor of origin, I could have
as easily chose to focus on the number of moves the elevator made to determine "optimal" solution. However, give this is 
simulation of real world events, it is perfectly conceivable to assume that customer wait time should supersede elevator
efficiency.   



### Running & Set Up

To install the requirements and run the project simply run the setup.py
file. 

``python setup.py``

The setup file should initialise a virtual environment, install the required dependencies, activate the virtual enviornment 
and run the view.py file.

If for some reason this fails at any point the project can be run manually assuming all requirements are meet by 

``python3 view.py``

As of now the setup.py file is fully functional on a mac OS system however it uses the subprocesses library which may 
mean that some of the shell commands may be different on your system.  