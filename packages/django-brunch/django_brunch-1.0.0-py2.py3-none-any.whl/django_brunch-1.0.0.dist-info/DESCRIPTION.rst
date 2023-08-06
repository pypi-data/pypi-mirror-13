
This replaces the `runserver` management command with a version that fires up a `brunch watch` process alongside the
Django development server to automatically recompile css and javascript. The brunch process is not interrupted when
the Django server reloads, but it will die when you shut down down the Django server.

`Full Documentation on GitHub <https://github.com/nshafer/django-brunch>`_


