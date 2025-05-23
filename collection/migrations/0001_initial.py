# Generated by Django 4.2.20 on 2025-04-15 00:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=50)),
                ('date_received', models.DateTimeField(auto_now_add=True)),
                ('is_favorite', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pokemons', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
