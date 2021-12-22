# Spydark webiste demo
### Watch the quick introduction [here](https://drive.google.com/file/d/16VAdNi0PbEuygGOfaDo-79JaJmKR4D1U/view?usp=sharing) 

### Watch the complete demo [here](https://drive.google.com/file/d/1zK4BMiNKIx8BeAub1K6BK8LZIEQkiu56/view?usp=sharing) 
<br>

# Steps to get running
### 1) Download the requirements:-

```
pip install -r requirements.txt
```

### 2) Open python terminal
```
import nltk
nltk.download()
```
_Download the 'popular' collection_
<br>
<br>

### 3) Download the weights file from [here](https://drive.google.com/file/d/195hwdBwI8qd4erD9whi64R4uTWuz9MvV/view?usp=sharing)
_Save the above weights file at \YOLOv3\spydark_yolo.weights_
<br>
<br>

### 4) Enter username and password for social media (Instagram) login in \crawler\utils.py
<br>

### 5) Create mongodb atlas account and enter driver code in \crawler\utils.py
<br>

### 6) Download Tor browser and configure Torcc hash password. 
#### Navigate to the folder containing tor.exe file and enter the following command in command prompt.
```
tor.exe --hash-password <hash_control_password> | more
```
#### Use the <hash_control_password> in \crawler\darkweb_crawler.py
<br>

### 7) Download latest chromedriver (for selenium) and save in \chromedriver_win32
<br>

### 8) Run the development server:-

```python
python manage.py runserver
```
  
### 9) Enter the localhost on your browser
