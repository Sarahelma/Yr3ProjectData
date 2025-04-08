# Yr3ProjectData
Repo to store data from drop out tests using NRF24l01P modules



## key datasets
* **13/02/2025** - initial range tests, no standardised method, but was useful in understanding how to formulate a python script to calculate success rate and packets per second. 

* **27/02/2025** - Was able to achieve 800m stable connection, however connector wobble starting causing issues on the way back

* **28/02/2025** - soon after setup one teensy board broke. 

* **19/03/2025** - first proper tests with accurately measured distances. measured at discrete intervals for 30 seconds at each data rate and power level. Issues with strange overlaping packets between different powerlevels at same timestamp. Either faulty switch or experimental errors by assistant. Discussed in report but not used as reliable source due to arbitarty nature of "selecting" which intervals to use

* **20/03/2025** - Better Whip attenna used at base station. counter used to log distance checkpoints. continous data stream. All at high power levels upto 350m

* **23/03/2025** - tests at home at 1m for different datarates and using dynamc payload

* **24/03/2025** - some tests with plans to test upto 1.5km along middlewood way. after some initial test location was deemed unsuitable because curvature+trees impede LOS. 

* **Live DTI** - live wireless CAN tests with DTI inverter. 


