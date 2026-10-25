\# MMA3001 Apple Tree Depth Interpolation



This project investigates the numerical interpolation of mission depth observations from an RGB-D apple tree dataset.



\## Objective



Compare the nearest neighbour interpolation with inverse distance weighting (IDW), focusing on accuracy, prediction coverage, and computation time.



\## Data



The original dataset is provided through google drive access from Monash University.



The experiments use 12 depth image observations across six tree identifiers and summer/winter conditions.



\## Methods



* Nearest neighbour interpolation
* Inverse distance weighting (8 neighbours)
* Random pixel validation
* 12 by 12 spatial block validation
* Common support accuracy comparison



\## How to run



Run the notebooks in order

1. notebooks/1\_Dataset.ipynb
2. notebooks/2\_Depth\_Metric.ipynb
3. notebooks/3\_Common\_Support\_Metric.ipynb
4. notebooks/4\_Result\_Visualisations.ipynb



notebook 1 requires access to the original shared dataset on google drive



notebooks 2 and 3 require the dataset ZIP produced by notebook 1 with authorised google drive access



notebook 4 requires access to the two results csv files from notebook 2 and 3



\## Results



The results folder contains experiment CSVs and figures comparing RMSE, MAE, prediction coverage, and runtime.



Camera calibration and ground truth annotation meanings have not been verified.



Calibrated 3D tree skeleton is not included in this project.



