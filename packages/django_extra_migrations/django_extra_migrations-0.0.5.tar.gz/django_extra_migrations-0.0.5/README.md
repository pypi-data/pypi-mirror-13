    pip install django_extra_migrations

# Resave

*Resave all records with calling save and signals events*

Create empty migration - ```./manage.py makemigrations %APP_NAME% --empty```

Open migration file ./%APP_NAME%/migrations/%MIGRATION_NAME%.py

###Import

    from django_extra_migrations.migrations import Resave
    
###Operation

    Resave("%APP_NAME%.%MODEL_NAME%"),
    
###Example:
  
    from __future__ import unicode_literals
    from django.db import models, migrations
    from django_extra_migrations.migrations import Resave, GrantPermissions


    class Migration(migrations.Migration):
        dependencies = [
            ('tree', '0078_auto_20151014_1500'),
        ]

    operations = [
        Resave("tree.Resource"),
    ]

---

#GrantPermissions

*Grant permissions to groups*

Create empty migration - ```./manage.py makemigrations %APP_NAME% --empty```

Open migration file ./%APP_NAME%/migrations/%MIGRATION_NAME%.py

###Import

    from django_extra_migrations.migrations import GrantPermissions
    
###Operation
    
    GrantPermissions(["%GROUP_NAME%"], (
        ("%APP_NAME%.%MODEL_NAME%", True), # IF true - grant ALL perms for this content type
        ("%APP_NAME%.%MODEL_NAME%", ["add_%LOWER_MODEL_NAME%"]),
        ("%APP_NAME%.%MODEL_NAME%", ["change_%LOWER_MODEL_NAME%"]),
        ("%APP_NAME%.%MODEL_NAME%", ["delete_%LOWER_MODEL_NAME%"]),
    )),
    
    
###Example:
  
    from __future__ import unicode_literals
    
    from django.db import models, migrations
    from django_extra_migrations.migrations import GrantPermissions
    
    
    class Migration(migrations.Migration):
        dependencies = [
            ('tree', '0078_auto_20151014_1500'),
        ]
    
        operations = [
            GrantPermissions(["Admins"], (
                ("tree.Resource", True),
                ("tree.ResourceFile", ["add_resourcefile"]),
            )),
        ]
