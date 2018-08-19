# Generated by Django 2.0.7 on 2018-08-04 00:20

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
            name='AgentData',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('timestamp', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=100)),
                ('monitor', models.CharField(max_length=250)),
                ('value', models.DecimalField(decimal_places=2, max_digits=50)),
            ],
            options={
                'verbose_name_plural': 'AgentData',
                'permissions': (('mon_admin', 'Monitoring Admin'),),
            },
        ),
        migrations.CreateModel(
            name='AgentEvent',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('eventdate', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
                ('monitor', models.CharField(max_length=250)),
                ('message', models.CharField(max_length=250)),
                ('status', models.BooleanField(default=True)),
                ('severity', models.CharField(choices=[('Critical', 'Critical'), ('Major', 'Major'), ('Warning', 'Warning'), ('Information', 'Information')], default='Information', max_length=11)),
                ('threshold', models.PositiveIntegerField()),
                ('compare', models.CharField(max_length=2)),
                ('timerange', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name_plural': 'AgentEvents',
                'permissions': (('mon_admin', 'Monitoring Admin'),),
            },
        ),
        migrations.CreateModel(
            name='AgentSystem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('timestamp', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=100)),
                ('osname', models.CharField(max_length=250)),
                ('osbuild', models.CharField(max_length=50)),
                ('osarchitecture', models.CharField(max_length=25)),
                ('domain', models.CharField(max_length=100)),
                ('processors', models.PositiveIntegerField()),
                ('memory', models.DecimalField(decimal_places=2, max_digits=10)),
                ('value', models.DecimalField(decimal_places=2, max_digits=50)),
            ],
            options={
                'verbose_name_plural': 'AgentSystem',
                'permissions': (('mon_admin', 'Monitoring Admin'),),
            },
        ),
        migrations.CreateModel(
            name='AgentThreshold',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('monitor', models.CharField(max_length=250)),
                ('severity', models.CharField(choices=[('Critical', 'Critical'), ('Major', 'Major'), ('Warning', 'Warning'), ('Information', 'Information')], default='Information', max_length=11)),
                ('threshold', models.PositiveIntegerField()),
                ('compare', models.CharField(max_length=2)),
                ('timerange', models.PositiveIntegerField()),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'AgentThresholds',
                'permissions': (('mon_admin', 'Monitoring Admin'),),
            },
        ),
        migrations.CreateModel(
            name='GlobalThreshold',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('monitor', models.CharField(max_length=250)),
                ('severity', models.CharField(choices=[('Critical', 'Critical'), ('Major', 'Major'), ('Warning', 'Warning'), ('Information', 'Information')], default='Information', max_length=11)),
                ('threshold', models.PositiveIntegerField()),
                ('compare', models.CharField(max_length=2)),
                ('timerange', models.PositiveIntegerField()),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'GlobalThresholds',
                'permissions': (('mon_admin', 'Monitoring Admin'),),
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('notify', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Subscriptions',
                'permissions': (('mon_admin', 'Monitoring Admin'),),
            },
        ),
    ]
