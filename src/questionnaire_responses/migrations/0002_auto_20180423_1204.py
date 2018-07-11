# Generated by Django 2.0.3 on 2018-04-23 09:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0001_initial'),
        ('questionnaire_responses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionnaireResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_description', models.TextField()),
                ('description1', models.TextField(blank=True, default='')),
                ('description2', models.TextField(blank=True, default='')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='questionnaire.Category')),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='questionnaire.Questionnaire')),
            ],
        ),
        migrations.CreateModel(
            name='ResponseResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=0)),
                ('qr', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='questionnaire_responses.QuestionnaireResult')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='questionnaire_responses.Response')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='questionnaireresult',
            unique_together={('questionnaire', 'category')},
        ),
    ]
