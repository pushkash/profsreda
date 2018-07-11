# Generated by Django 2.0.3 on 2018-04-23 05:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(max_length=100, verbose_name='Текст варианта')),
            ],
            options={
                'verbose_name': 'Вариант ответа',
                'verbose_name_plural': 'Варианты ответов',
            },
        ),
        migrations.CreateModel(
            name='AnswerType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тип ответа',
                'verbose_name_plural': 'Типы ответов',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=400, unique=True, verbose_name='Название категории')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст вопроса')),
                ('sort_id', models.PositiveIntegerField(verbose_name='Порядковый номер в опроснике')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='questionnaire.Category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=400, unique=True, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('answers_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='questionnaire.AnswerType', verbose_name='Тип ответов')),
            ],
            options={
                'verbose_name': 'Анкета теста',
                'verbose_name_plural': 'Анкеты тестов',
            },
        ),
        migrations.AddField(
            model_name='question',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='questionnaire.Questionnaire', verbose_name='Опрос'),
        ),
        migrations.AddField(
            model_name='answerchoice',
            name='answer_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='questionnaire.AnswerType'),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together={('sort_id', 'questionnaire')},
        ),
        migrations.AlterUniqueTogether(
            name='answerchoice',
            unique_together={('answer_type', 'choice')},
        ),
    ]
