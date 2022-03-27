from django.db import models
import datetime
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class TypeOfOrgUnit(models.TextChoices):
    """
    Виды структурных единиц
    """
    DIVISION = 'dv', 'Обособленное подразделение'
    OFFICIAL = 'of', 'Куратор'
    BODY = 'bd', 'Орган'


class TypeOfReorganization(models.TextChoices):
    """
    Виды структурных изменений (реорганизации)
    """
    CREATION = 'cr', 'Создание'
    ABOLITION = 'ab', 'Упразднение'
    REASSIGN = 'rs', 'Переподчинение'
    RENAME = 'rn', 'Переименование'
    MERGER = 'mr', 'Слияние'
    DIVISION = 'dv', 'Разделение'


class Change(models.Model):
    """
    Изменение структуры (реорганизация)
    """

    # Вид реорганизации
    change = models.CharField(
        choices=TypeOfReorganization.choices,
        max_length=2,
        verbose_name='Вид реорганизации',
        blank=False,
    )

    # Дата события
    date = models.DateField(
        verbose_name='Дата события',
        default=datetime.date.today,
        blank=False,
    )

    # Событие
    event = models.CharField(
        verbose_name='Событие',
        max_length=64,
        null=True,
        blank=False,
    )

    # Описание события
    note = models.TextField(
        verbose_name='Описание события',
        null=True,
        blank=True,
    )

    # Поле для поиска (содержит запись события в нижнем регистре)
    search_line = models.CharField(
        verbose_name='Поле для поиска',
        help_text='Содержит запись события в нижнем регистре',
        max_length=254,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Изменение структуры'
        verbose_name_plural = 'Структурные изменения'
        ordering = [
            '-date',
            'change',
            'event',
        ]

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.change}, {self.date.strftime("%Y.%m.%d")}, "{self.event}")')

    def __str__(self):
        return f'{self.date.strftime("%Y.%m.%d")} {self.event}'


# Установить значения для автоматических полей
@receiver(pre_save, sender=Change)
def change_pre_save(instance, **kwargs):
    # Сформировать поле поиска
    instance.search_line = f'{instance.event.lower()}'[:254]


class OrgUnit(models.Model):
    """
    Подразделение
    """

    # Наименование
    name = models.CharField(
        verbose_name='Наименование',
        help_text='Полное наименование подразделения',
        max_length=200,
        null=True,
        blank=False,
    )

    # Сокращённое наименование
    short_name = models.CharField(
        verbose_name='Аббревиатура',
        help_text='Краткое наименование подразделения',
        max_length=32,
        null=True,
        blank=True,
    )

    # Код подразделения
    structure_code = models.CharField(
        verbose_name='Код',
        help_text='Код структурного подразделения',
        max_length=32,
        null=True,
        blank=True,
    )

    # Вид подразделения
    type_of_unit = models.CharField(
        choices=TypeOfOrgUnit.choices,
        max_length=2,
        verbose_name='Вид',
        help_text='Вид подразделения',
        default='dv',
        blank=False,
    )

    # Причина создания
    reason_creation = models.ForeignKey(
        Change,
        verbose_name='Событие',
        related_name='org_unit_creation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Дата создания (устанавливается по причине создания)
    date_creation = models.DateField(
        verbose_name='Дата создания',
        null=True,
        blank=True,
    )

    # Причина упразднения
    reason_abolition = models.ForeignKey(
        Change,
        verbose_name='Событие',
        related_name='org_unit_abolition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Дата упразднения (устанавливается по причине упразднения)
    date_abolition = models.DateField(
        verbose_name='Дата упразднения',
        null=True,
        blank=True,
    )

    # Подразделение существует или упразднено? (устанавливается по причине упразднения)
    exist = models.BooleanField(
        verbose_name='Статус',
        help_text='Подразделение существует или упразднено?',
        default=True,
    )

    # Подчинение
    parent = models.ForeignKey(
        'self',
        verbose_name='Подчинение',
        related_name='org_unit_parent',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    # Поле для поиска (содержит другие ключевые поля в нижнем регистре)
    search_line = models.CharField(
        verbose_name='Поле для поиска',
        help_text='Содержит все ключевые поля в нижнем регистре',
        max_length=254,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = [
            'name',
        ]
        unique_together = ['name', 'reason_creation']

    def __repr__(self):
        result = f'{self.__class__.__name__}('

        if self.short_name:
            result += f'{self.short_name}, '
        else:
            result += f'{self.name}, '

        return result

    def __str__(self):
        return self.name


# Установить значения для автоматических полей
@receiver(pre_save, sender=OrgUnit)
def orgunit_pre_save(instance, **kwargs):
    # Получить дату создания подразделения
    if instance.reason_creation:
        instance.date_creation = instance.reason_creation.__getattribute__('date')

    # Получить дату упразднения подразделения
    if instance.reason_abolition:
        instance.date_abolition = instance.reason_abolition.__getattribute__('date')

    # Определить статус подразделения
    if instance.reason_abolition:
        instance.exist = False
    else:
        instance.exist = True

    # Сформировать поле поиска
    sl = f''
    if instance.short_name:
        sl += f'{instance.short_name.lower()}'
    if instance.structure_code:
        sl += f'{instance.structure_code.lower()}'
    if instance.name:
        sl += f'{instance.name.lower()}'
    instance.search_line = sl[:254]


# Корректировка полей даты создания и упразднения подразделения при изменении записи реорганизации
@receiver(post_save, sender=Change)
def update_orgunit_date_after_change_post_save(instance, **kwargs):
    # Корректировка даты создания подразделения
    for ou in instance.org_unit_creation.all():
        ou.save()

    # Корректировка даты упразднения подразделения
    for ou in instance.org_unit_abolition.all():
        ou.save()
