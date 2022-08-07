# Generated by Django 4.0.6 on 2022-08-07 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_document_project_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='is_folder_or_file',
            field=models.IntegerField(default=0, verbose_name='文件或者文件夹'),
        ),
        migrations.AddField(
            model_name='document',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='document.document', verbose_name='父级文件夹'),
        ),
    ]
