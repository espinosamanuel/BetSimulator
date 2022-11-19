
# BetSimulator

A backtester for soccer betting strategies written in Python.




## Installation

This project is compatible with Python3. To install BetSimulator clone this repository on your local machine.
    
## Quickstart

At this stage, data are provided within the project. In the future, the data will be automatically managed by BetSimulator and downloaded at runtime. 

First, it is necessary to process the raw data by going to organize them into a format that can be used by the back-tester.

The process command will do the job:
```
python bet_simulator.py process
```
This step should be performed only the first time and each time there is a change in the raw data.

Test the dummy strategy using the test command:
```
python bet_simulator.py test dummy
```
If everything worked properly, the output folder should contain the test result.
There is nothing left to do but write other strategies and use them instead of dummy.
## Strategies Guide
A strategy is a .py file to be placed inside the strategies directory.
Each file must contain a Strategy class that extends the strategies.base_strategy.BaseStrategy class. 
The Strategy class must implement all the abstract methods of BaseStrategy:
- accept
- aggregate
- select_out
- get_bet_amount

For more information on implementing the methods required for the strategy, see the documentation.
## Documentation

[BetSimulator Docs](https://espinosamanuel.github.io/BetSimulator/)

