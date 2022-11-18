# Eda.yandex.ru Parser
Completed freelance order. The customer needed a parser for pictures from Yandex food services with a simple graphical interface for Windows.
## Usage:
To download images, you need to insert a link to the Yandex food service into the text field and click the **"Download"** button.
![img.png](readme_img1.png)
Images will start loading, please wait. Images are loaded asynchronously, so it won't take long.
![img_1.png](readme_img2.png)
You will see a message when all images have been uploaded (**"Image upload completed!"**).
![img_2.png](readme_img3.png)
By default, images are saved to the current user's *Downloads* folder (this can be changed in the code). Images are saved with the same names as on the service itself (with the exception of characters that cannot be used for Windows file names, as well as duplicate names). If the file names are duplicated , then a number is appended to them.
![img_3.png](readme_img6.png)