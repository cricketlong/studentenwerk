# Generated by Django 2.0.1 on 2018-05-25 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speiseplan', '0003_auto_20180525_2241'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='meal_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='mealdate',
            name='date_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='mealdate',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
