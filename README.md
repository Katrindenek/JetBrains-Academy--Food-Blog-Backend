## Food Blog Application

This application is a simple food blog application that allows users to create and manage recipes and ingredients. It uses SQLite database to store data.
The application is a part of [JetBrains Academy](https://hyperskill.org/projects/167) course for "Databases with SQL and Python course" track.

### Installation

1. Clone the repository:
```
git clone https://github.com/Katrindenek/JetBrains-Academy--Food-Blog-Backend.git
```

### Usage

1. Create a new database:
```
python food_blog.py food_blog.db
```
2. Fill in the recipe name, the description, choose the meal and provide the ingredients in the format `quantity measure ingredient`.
3. Now you can search your recipes by ingredients and meals:
```
python food_blog.py food_blog.db --ingredients="<ingredients splitted with comma>" --meals="<breakfast,brunch,lunch,supper>"
```
