# RCD
Implementation of Recursive Constraint Demotion (Tesar & Smolensky 2000)

## Running the script
The script can be run directly from the command line. The script takes as an argument the name of a `.csv` file and prints the stratified ranking.

The input file should be of a form seen in typical OTSoft format. See the examples (e.g. `feeding_interaction.csv` or `palatalization.csv`) for specific examples.

In order to see the code in action, pull the code and type the following command in the command line:

```
python3 RCD.py palatalization.csv
```
