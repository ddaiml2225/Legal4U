Create a database named "BTechProject102db".

## How to Run

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Note:

--We are using Bootstrap version 4.0.0. Bookmark this in your browser otherwise it won't work if you use some other versions.
Link : https://getbootstrap.com/docs/4.0/getting-started/introduction/

--Change DB info from manage.py environment variables.

-- `mysite.log` is for maintaining error and debug logs during hosting.

## Database Abbreviations/Formatting:

Gender:
Male: "" Female: None

Role:
Lawyer: "" Aggrieved: None

Verification:
Verified: "" Unverified: None

## Additional query to run on database:
alter table user add column nickname varchar(255) unique after name;