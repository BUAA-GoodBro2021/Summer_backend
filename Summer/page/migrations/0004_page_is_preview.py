# Generated by Django 4.1 on 2022-08-07 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0003_alter_page_page_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='is_preview',
            field=models.BooleanField(default=False, verbose_name='是否预览'),
        ),
    ]