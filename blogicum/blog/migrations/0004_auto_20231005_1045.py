# Generated by Django 3.2.16 on 2023-10-05 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20231002_1202'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('pub_date',), 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
        migrations.AlterField(
            model_name='category',
            name='title',
            field=models.CharField(max_length=256, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='blog.category', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='post',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='blog.location', verbose_name='Местоположение'),
        ),
    ]
