# Fire_Emblem
 Data analysis of Fire Emblem Engage character progression throughout levelling based on promotion class chosen.
 
## Installation:
Click on "Code" (top right) and download and extract to a local folder on your PC.
 
The following instructions are to be used within the [Anaconda terminal] (https://docs.anaconda.com/anaconda/user-guide/getting-started/), although there are other ways too, but this is one of the simplest! :)
 
 ```.bash
 # ----> Navigate to the folder you downloaded the files to.
 # Create virtual environment call "fire_emblem":
 conda create --name fire_emblem
 # Activate environment:
 conda activate fire_emblem
 # Install the pip package which will help install other packages in reqs.txt
 conda install pip
 pip install -r reqs.txt
 # Run Jupyter notebook
 jupyter notebook

```
 
## Example bar chart comparison between characters:

<p align="center">
<img src="https://github.com/williamdee1/Fire_Emblem/blob/main/media/bar_ex.PNG" width=75% height=75% class="center">
</p>


## Example scatterplot comparison of character's metrics at a specific level:

<p align="center">
<img src="https://github.com/williamdee1/Fire_Emblem/blob/main/media/scatter_ex.PNG" width=75% height=75% class="center">
</p>

Hope this helps some people, I had fun making it! Let me know in Issues if there are any problems.
