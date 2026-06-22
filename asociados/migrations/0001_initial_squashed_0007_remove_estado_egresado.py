import uuid

import django.db.migrations.operations.special
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def crear_ciclos_para_inscripciones(apps, schema_editor):
    CicloLectivo = apps.get_model("asociados", "CicloLectivo")
    InscripcionCurso = apps.get_model("asociados", "InscripcionCurso")
    anios = (
        InscripcionCurso.objects.exclude(ciclo_lectivo__isnull=True)
        .values_list("ciclo_lectivo", flat=True)
        .distinct()
    )
    for anio in anios:
        CicloLectivo.objects.get_or_create(anio=anio)


def asignar_ciclos_a_inscripciones(apps, schema_editor):
    CicloLectivo = apps.get_model("asociados", "CicloLectivo")
    InscripcionCurso = apps.get_model("asociados", "InscripcionCurso")
    ciclos_por_anio = {ciclo.anio: ciclo for ciclo in CicloLectivo.objects.all()}
    for inscripcion in InscripcionCurso.objects.all():
        ciclo = ciclos_por_anio[inscripcion.ciclo_lectivo_anio]
        inscripcion.ciclo_lectivo_id = ciclo.id
        inscripcion.save(update_fields=["ciclo_lectivo"])


def convertir_egresados_en_inactivos(apps, schema_editor):
    Asociado = apps.get_model("asociados", "Asociado")
    Asociado.objects.filter(estado="egresado").update(estado="inactivo")


class Migration(migrations.Migration):

    replaces = [('asociados', '0001_initial'), ('asociados', '0002_ciclolectivo_alter_inscripcioncurso_options_and_more'), ('asociados', '0003_remove_curso_colegio_alter_curso_options_and_more'), ('asociados', '0004_alter_curso_anio_alter_curso_curso'), ('asociados', '0005_delete_inscripcioncurso'), ('asociados', '0006_remove_asociado_fecha_nacimiento_asociado_direccion'), ('asociados', '0007_remove_estado_egresado')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Colegio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, unique=True)),
                ('direccion', models.CharField(blank=True, max_length=255)),
                ('telefono', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Colegio',
                'verbose_name_plural': 'Colegios',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('activo', models.BooleanField(default=True)),
                ('colegio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cursos', to='asociados.colegio')),
            ],
            options={
                'verbose_name': 'Curso',
                'verbose_name_plural': 'Cursos',
                'ordering': ['colegio__nombre', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Asociado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('dni', models.CharField(max_length=20, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('telefono', models.CharField(blank=True, max_length=50)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('tipo', models.CharField(choices=[('asociado', 'Asociado'), ('adherente', 'Adherente')], max_length=20)),
                ('numero_asociado', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('token_credencial', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo'), ('egresado', 'Egresado')], default='activo', max_length=20)),
                ('fecha_alta', models.DateField()),
                ('fecha_inicio_cobro', models.DateField()),
                ('fecha_baja', models.DateField(blank=True, null=True)),
                ('motivo_baja', models.CharField(blank=True, max_length=255)),
                ('usuario', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asociado', to=settings.AUTH_USER_MODEL)),
                ('curso_actual', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asociados_actuales', to='asociados.curso')),
            ],
            options={
                'verbose_name': 'Asociado',
                'verbose_name_plural': 'Asociados',
                'ordering': ['apellido', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='InscripcionCurso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ciclo_lectivo', models.PositiveIntegerField()),
                ('activa', models.BooleanField(default=True)),
                ('fecha_desde', models.DateField()),
                ('fecha_hasta', models.DateField(blank=True, null=True)),
                ('asociado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inscripciones', to='asociados.asociado')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inscripciones', to='asociados.curso')),
            ],
            options={
                'verbose_name': 'Inscripcion a curso',
                'verbose_name_plural': 'Inscripciones a curso',
                'ordering': ['-ciclo_lectivo', '-fecha_desde'],
            },
        ),
        migrations.AddIndex(
            model_name='curso',
            index=models.Index(fields=['colegio', 'activo'], name='asociados_c_colegio_c5129a_idx'),
        ),
        migrations.AddConstraint(
            model_name='curso',
            constraint=models.UniqueConstraint(fields=('colegio', 'nombre'), name='uniq_curso_por_colegio'),
        ),
        migrations.AddIndex(
            model_name='asociado',
            index=models.Index(fields=['estado', 'tipo'], name='asociados_a_estado_fc7c14_idx'),
        ),
        migrations.AddIndex(
            model_name='asociado',
            index=models.Index(fields=['numero_asociado'], name='asociados_a_numero__2252d2_idx'),
        ),
        migrations.AddIndex(
            model_name='asociado',
            index=models.Index(fields=['fecha_inicio_cobro'], name='asociados_a_fecha_i_3ae177_idx'),
        ),
        migrations.AddIndex(
            model_name='inscripcioncurso',
            index=models.Index(fields=['asociado', 'activa'], name='asociados_i_asociad_263939_idx'),
        ),
        migrations.AddIndex(
            model_name='inscripcioncurso',
            index=models.Index(fields=['ciclo_lectivo'], name='asociados_i_ciclo_l_767aa4_idx'),
        ),
        migrations.AddConstraint(
            model_name='inscripcioncurso',
            constraint=models.UniqueConstraint(fields=('asociado', 'curso', 'ciclo_lectivo', 'fecha_desde'), name='uniq_inscripcion_historial'),
        ),
        migrations.CreateModel(
            name='CicloLectivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anio', models.PositiveSmallIntegerField(help_text='Año del ciclo lectivo.', unique=True, verbose_name='año')),
            ],
            options={
                'verbose_name': 'Ciclo lectivo',
                'verbose_name_plural': 'Ciclos lectivos',
                'ordering': ['-anio'],
            },
        ),
        migrations.RunPython(
            code=crear_ciclos_para_inscripciones,
            reverse_code=django.db.migrations.operations.special.RunPython.noop,
        ),
        migrations.RemoveConstraint(
            model_name='inscripcioncurso',
            name='uniq_inscripcion_historial',
        ),
        migrations.RemoveIndex(
            model_name='inscripcioncurso',
            name='asociados_i_ciclo_l_767aa4_idx',
        ),
        migrations.RenameField(
            model_name='inscripcioncurso',
            old_name='ciclo_lectivo',
            new_name='ciclo_lectivo_anio',
        ),
        migrations.AddField(
            model_name='inscripcioncurso',
            name='ciclo_lectivo',
            field=models.ForeignKey(blank=True, help_text='Año lectivo de esta inscripción.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inscripciones', to='asociados.ciclolectivo', verbose_name='ciclo lectivo'),
        ),
        migrations.RunPython(
            code=asignar_ciclos_a_inscripciones,
            reverse_code=django.db.migrations.operations.special.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='inscripcioncurso',
            name='ciclo_lectivo',
            field=models.ForeignKey(help_text='Año lectivo de esta inscripción.', on_delete=django.db.models.deletion.PROTECT, related_name='inscripciones', to='asociados.ciclolectivo', verbose_name='ciclo lectivo'),
        ),
        migrations.RemoveField(
            model_name='inscripcioncurso',
            name='ciclo_lectivo_anio',
        ),
        migrations.AlterModelOptions(
            name='inscripcioncurso',
            options={'ordering': ['-ciclo_lectivo__anio', '-fecha_desde'], 'verbose_name': 'Inscripción a curso', 'verbose_name_plural': 'Inscripciones a curso'},
        ),
        migrations.AlterField(
            model_name='colegio',
            name='activo',
            field=models.BooleanField(default=True, help_text='Indica si el colegio participa activamente en el sistema.', verbose_name='activo'),
        ),
        migrations.AlterField(
            model_name='colegio',
            name='direccion',
            field=models.CharField(blank=True, help_text='Dirección física del colegio.', max_length=255, null=True, verbose_name='dirección'),
        ),
        migrations.AlterField(
            model_name='colegio',
            name='email',
            field=models.EmailField(blank=True, help_text='Correo de contacto del colegio.', max_length=254, null=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='colegio',
            name='nombre',
            field=models.CharField(help_text='Nombre de la institución educativa.', max_length=150, unique=True, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='colegio',
            name='telefono',
            field=models.CharField(blank=True, help_text='Teléfono de contacto del colegio.', max_length=50, null=True, verbose_name='teléfono'),
        ),
        migrations.AlterField(
            model_name='curso',
            name='activo',
            field=models.BooleanField(default=True, help_text='Indica si el curso está activo en el sistema.', verbose_name='activo'),
        ),
        migrations.AlterField(
            model_name='curso',
            name='colegio',
            field=models.ForeignKey(help_text='Colegio al que pertenece el curso.', on_delete=django.db.models.deletion.PROTECT, related_name='cursos', to='asociados.colegio', verbose_name='colegio'),
        ),
        migrations.AlterField(
            model_name='curso',
            name='nombre',
            field=models.CharField(help_text='Nombre del curso, por ejemplo: 1° 1°.', max_length=50, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='inscripcioncurso',
            name='activa',
            field=models.BooleanField(default=True, help_text='Indica si esta es la inscripción vigente del asociado.', verbose_name='activa'),
        ),
        migrations.AlterField(
            model_name='inscripcioncurso',
            name='asociado',
            field=models.ForeignKey(help_text='Asociado inscripto en el curso.', on_delete=django.db.models.deletion.CASCADE, related_name='inscripciones', to='asociados.asociado', verbose_name='asociado'),
        ),
        migrations.AlterField(
            model_name='inscripcioncurso',
            name='curso',
            field=models.ForeignKey(help_text='Curso en el que está inscripto el asociado.', on_delete=django.db.models.deletion.PROTECT, related_name='inscripciones', to='asociados.curso', verbose_name='curso'),
        ),
        migrations.AlterField(
            model_name='inscripcioncurso',
            name='fecha_desde',
            field=models.DateField(help_text='Fecha de inicio de esta inscripción.', verbose_name='fecha desde'),
        ),
        migrations.AlterField(
            model_name='inscripcioncurso',
            name='fecha_hasta',
            field=models.DateField(blank=True, help_text='Fecha de fin de esta inscripción. Vacío si sigue activa.', null=True, verbose_name='fecha hasta'),
        ),
        migrations.AddIndex(
            model_name='inscripcioncurso',
            index=models.Index(fields=['ciclo_lectivo'], name='asociados_i_ciclo_l_af39a3_idx'),
        ),
        migrations.AddConstraint(
            model_name='inscripcioncurso',
            constraint=models.UniqueConstraint(fields=('asociado', 'curso', 'ciclo_lectivo', 'fecha_desde'), name='uniq_inscripcion_historial'),
        ),
        migrations.RemoveConstraint(
            model_name='curso',
            name='uniq_curso_por_colegio',
        ),
        migrations.RemoveIndex(
            model_name='curso',
            name='asociados_c_colegio_c5129a_idx',
        ),
        migrations.RemoveField(
            model_name='curso',
            name='colegio',
        ),
        migrations.RemoveField(
            model_name='curso',
            name='nombre',
        ),
        migrations.AlterModelOptions(
            name='curso',
            options={'ordering': ['division', 'anio', 'curso', 'turno'], 'verbose_name': 'Curso', 'verbose_name_plural': 'Cursos'},
        ),
        migrations.AddField(
            model_name='curso',
            name='anio',
            field=models.CharField(blank=True, default='', help_text='Año que cursa, ej: 1ro, 2do, 3ro.', max_length=10, verbose_name='año'),
        ),
        migrations.AddField(
            model_name='curso',
            name='curso',
            field=models.CharField(blank=True, default='', help_text='División o número de curso, ej: 1ra, 2da, única.', max_length=10, verbose_name='curso'),
        ),
        migrations.AddField(
            model_name='curso',
            name='division',
            field=models.CharField(choices=[('CB', 'Ciclo Básico'), ('CS', 'Ciclo Superior')], default='CB', help_text='Ciclo al que pertenece: CB (Ciclo Básico) o CS (Ciclo Superior).', max_length=2, verbose_name='división'),
        ),
        migrations.AddField(
            model_name='curso',
            name='turno',
            field=models.CharField(choices=[('TM', 'Turno Mañana'), ('TT', 'Turno Tarde')], default='TM', help_text='Turno: TM (Turno Mañana) o TT (Turno Tarde).', max_length=2, verbose_name='turno'),
        ),
        migrations.AddConstraint(
            model_name='curso',
            constraint=models.UniqueConstraint(fields=('anio', 'curso', 'division', 'turno'), name='uniq_curso'),
        ),
        migrations.DeleteModel(
            name='Colegio',
        ),
        migrations.AlterField(
            model_name='curso',
            name='anio',
            field=models.CharField(help_text='Año que cursa, ej: 1ro, 2do, 3ro.', max_length=10, verbose_name='año'),
        ),
        migrations.AlterField(
            model_name='curso',
            name='curso',
            field=models.CharField(help_text='División o número de curso, ej: 1ra, 2da, única.', max_length=10, verbose_name='curso'),
        ),
        migrations.DeleteModel(
            name='InscripcionCurso',
        ),
        migrations.RemoveField(
            model_name='asociado',
            name='fecha_nacimiento',
        ),
        migrations.AddField(
            model_name='asociado',
            name='direccion',
            field=models.CharField(blank=True, help_text='Domicilio del asociado.', max_length=255, verbose_name='dirección'),
        ),
        migrations.RunPython(
            code=convertir_egresados_en_inactivos,
            reverse_code=django.db.migrations.operations.special.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='asociado',
            name='estado',
            field=models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo', max_length=20),
        ),
    ]
