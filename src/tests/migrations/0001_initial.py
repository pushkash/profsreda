# Generated by Django 2.0.1 on 2018-07-17 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('heroes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(help_text='Текст ответа', max_length=100, verbose_name='Ответ')),
            ],
            options={
                'verbose_name': 'Тест',
                'verbose_name_plural': 'Тесты',
            },
        ),
        migrations.CreateModel(
            name='AnswerCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(help_text='Текст ответа', max_length=100, verbose_name='Ответ')),
                ('weight', models.PositiveIntegerField(help_text='Коэффициент, с которым ответ учитывается при подсчёте результата', verbose_name='Коэффициент')),
            ],
            options={
                'verbose_name': 'Ответ-Категория',
                'verbose_name_plural': 'Пары Ответ-Категория',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название категории', max_length=100, verbose_name='Название')),
                ('short_description', models.TextField(help_text='Краткое описание категории', max_length=1000, verbose_name='Описание')),
                ('long_description', models.TextField(blank=True, help_text='Развёрнутое описание категории', max_length=10000, null=True, verbose_name='Развернутое описание')),
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
                ('text', models.CharField(help_text='Текст вопроса', max_length=100, verbose_name='Вопрос')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название теста', max_length=100, verbose_name='Название')),
                ('description', models.TextField(help_text='Описание теста', max_length=1000, verbose_name='Описание')),
                ('image', models.ImageField(help_text='Обложка теста', upload_to='media/test_images/', verbose_name='Обложка')),
            ],
            options={
                'verbose_name': 'Тест',
                'verbose_name_plural': 'Тесты',
            },
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.ForeignKey(help_text='Предмет, полученный в награду за прохождение теста', on_delete=django.db.models.deletion.DO_NOTHING, to='heroes.Item', verbose_name='Награда')),
            ],
            options={
                'verbose_name': 'Результат теста',
                'verbose_name_plural': 'Результаты тестов',
            },
        ),
        migrations.CreateModel(
            name='TestSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_finished', models.BooleanField(default=False, help_text='Значение, указывающее, закончена ли тест сессия', verbose_name='Закончена')),
                ('last_answered_question', models.ForeignKey(help_text='Последний вопрос, на который ответил пользователь', on_delete=django.db.models.deletion.DO_NOTHING, to='tests.Question', verbose_name='Последний отвеченный вопрос')),
                ('test', models.ForeignKey(help_text='Тест, к которому относиться сессия', on_delete=django.db.models.deletion.CASCADE, to='tests.Test', verbose_name='Тест')),
                ('user', models.ForeignKey(help_text='Пользователь, проходящий тест', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Тестируемый')),
            ],
            options={
                'verbose_name': 'Тест сессия',
                'verbose_name_plural': 'Тест сессии',
            },
        ),
        migrations.AddField(
            model_name='testresult',
            name='test_session',
            field=models.ForeignKey(help_text='Тест сессия, которой соответствует результат', on_delete=django.db.models.deletion.DO_NOTHING, to='tests.TestSession', verbose_name='Тест сессия'),
        ),
        migrations.AddField(
            model_name='question',
            name='test',
            field=models.ForeignKey(help_text='Тест, к которому относится вопрос', on_delete=django.db.models.deletion.CASCADE, to='tests.Test', verbose_name='Тест'),
        ),
        migrations.AddField(
            model_name='category',
            name='test',
            field=models.ForeignKey(help_text='Тест, определяющий данную категорию', on_delete=django.db.models.deletion.CASCADE, to='tests.Test', verbose_name='Тест'),
        ),
        migrations.AddField(
            model_name='answercategory',
            name='category',
            field=models.ForeignKey(help_text='Категория, соответствующая ответу', on_delete=django.db.models.deletion.CASCADE, to='tests.Category', verbose_name='Категория'),
        ),
        migrations.AddField(
            model_name='answercategory',
            name='question',
            field=models.ForeignKey(help_text='Соответствующий ответу вопрос', on_delete=django.db.models.deletion.CASCADE, to='tests.Question', verbose_name='Вопрос'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(help_text='Вопрос, к которому относится ответ', on_delete=django.db.models.deletion.CASCADE, to='tests.Question', verbose_name='Вопрос'),
        ),
        migrations.AddField(
            model_name='answer',
            name='test_session',
            field=models.ForeignKey(help_text='Тест сессия, в которую был сделан ответ', on_delete=django.db.models.deletion.CASCADE, to='tests.TestSession', verbose_name='Тест сессия'),
        ),
    ]
