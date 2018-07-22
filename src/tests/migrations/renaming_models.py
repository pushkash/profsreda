from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel('Answer', 'Response'),
        migrations.RenameModel('AnswerCategory', 'Answer'),
    ]
