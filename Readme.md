# Readme

## Data Analyst (1040) submission by Adrian Diaz

This Readme file explains how to run Run\_All.bat included in this submission package.

### Assumptions:

1) The operating system is Windows 11\.  
2) Python 3.14 (with pip included in its installation) and R 4.4.3 will be used to run these programs. Python was installed for all users so this assumes having admin privileges.  
3) Both installations are clean.  
4) Any other typical required programs are installed.  
5) There is Internet access.

### Scripts included in the submission:

1) **IADB\_process.py:** Pulls the data from the IADB’s website and preprocesses it so it is left ready or almost ready for fitting models. The main output is a CSV file with the data in wide form that will be used for fitting models.  
2) **IADB\_fit.R:** Does some last-minute data processing (reads the CSV output from IADB\_process.py, so it needs to convert some variables to factors) and fits models. This program also installs any required R packages.  
3) **Run\_All.bat:** Installs the necessary Python packages using pip, runs IADB\_process.py and IADB\_fit.R

### Other inputs:

1) **reqs.txt:** Includes all Python packages (with their versions) that will be installed by pip.

### Outputs:

1) **corr\_heatmap.jpeg:** The heatmap of the correlation matrix of the regressors.  
2) **corr\_matrix.csv:** The correlation matrix of the regressors.  
3) **country\_counts.csv:** The number of cases in each country, before dropping those countries with few cases.  
4) **year\_counts.csv:** The number of cases for each year, after the countries were dropped. No years were dropped as all remaining years have at least 10 cases.  
5) **missingness\_variable.csv:** The percentage of missing observations of the independent variables under consideration, after those cases with missing values for the dependent variable were dropped.  
6) **Rplots.pdf:** Diagnostic plots for all the regressions that were fit.  
7) **summary\_full\_linear.csv:** Output of the OLS regression using the full model  
8) **summary\_step\_linear.csv:** Output of the OLS regression model after doing stepwise selection.  
9) **summary\_full\_beta.csv:** Output of the Beta regression using the full model.  
10) **summary\_step\_beta.csv:** Output of the Beta regression after doing backwards selection.  
11) **summary\_final\_beta.csv:** Output of the Beta regression used in the analysis.
12) **summary\_stats.csv:** Summary statistics of data_final.csv.
13) **Run\_All.log:** Log of the run of Run_All.bat.

### Github:

Github available at: https://github.com/adiazp/Data-Analyst-1040-IADB-2025