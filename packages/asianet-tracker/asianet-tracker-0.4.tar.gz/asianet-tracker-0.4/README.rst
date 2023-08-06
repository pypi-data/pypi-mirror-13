=====
Asianet-tracker
=====

Asianet-tracker is a simple Django app to log data from URL visits Web-based polls.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "asianet-tracker" to your INSTALLED_APPS setting like this::

       INSTALLED_APPS = [
               ...
                       'asianet-tracker',
                           ]

2. Run `python manage.py migrate` to create the asianet-tracker models.

3. Start the development server and visit http://127.0.0.1:8000/

4. From views.py import track_this to include it in URLS you need to track
