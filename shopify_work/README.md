# Flask Template
---

```
usage: manage.py [-h] [-runserver] [-host HOST] [-port PORT] [-deploy] [-cleardb] [-addadmin] [-changepassword] [-getadmintoken] [-getdummy]

Run this server

options:

  -h, --help       show this help message and exit

Flask Application:

  -runserver       Run Flask Application with default host and port, Can Change in -host and -port

  -host HOST       Change the host ip of Flask Server, To Access it on other PC's, Use 0.0.0.0

  -port PORT       Enter the Port Manually

Database Functions:

  -deploy          It initializes the db models in the models.py file.... stamps it, migrates it, and upgrades it

  -cleardb         Clears the DB

Admin Functions:

  -addadmin        Adds An Admin

  -changepassword  Changes Admin Password

  -getadmintoken   Gets Admin Token

Testing:

  -getdummy        Gets Test Dummy Information for Testing Purpose Only

Have Fun
```
