# NutriView

Thanks for stopping by! Check us out here: https://nutriview.space

Authored by @sctigercat1, @NSCakir, & @MohtionX at CUHackIt 2020.

Materials used: Django, Python, AWS Rekognition, and the USDA's FoodData API (https://fdc.nal.usda.gov/api-guide.html).

---

## Usage

To start:

1. Create a file called local_settings.py in the nutriview folder. You will need to get keys for the APIs of both AWS and the USDA. It should resemble the following:

```
AWS_SERVER_PUBLIC_KEY = ""
AWS_SERVER_SECRET_KEY = ""
USDA_API_KEY = ""
```

2. Run the following commands:

```
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```