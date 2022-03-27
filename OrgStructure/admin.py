from django.contrib import admin
from . import models
import random


# Вывод подразделений, созданных в результате структурного изменения
class OrgUnitCreationInline(admin.TabularInline):
    model = models.OrgUnit
    fk_name = 'reason_creation'
    fields = (
        'exist',
        'structure_code',
        'short_name',
        'name',
        'type_of_unit',
    )
    readonly_fields = (
        'exist',
        'structure_code',
        'short_name',
        'name',
        'type_of_unit',
    )
    extra = 0
    verbose_name_plural = 'Созданные подразделения'
    can_delete = False
    can_add = False
    show_change_link = True

    def has_add_permission(self, request, obj): return False


# Вывод подразделений, упразднённых в результате структурного изменения
class OrgUnitAbolitionInline(admin.TabularInline):
    model = models.OrgUnit
    fk_name = 'reason_abolition'
    fields = (
        'exist',
        'structure_code',
        'short_name',
        'name',
        'type_of_unit',
    )
    readonly_fields = (
        'exist',
        'structure_code',
        'short_name',
        'name',
        'type_of_unit',
    )
    extra = 0
    verbose_name_plural = 'Упразднённые подразделения'
    can_delete = False
    can_add = False
    show_change_link = True

    def has_add_permission(self, request, obj): return False


@admin.register(models.Change)
class ChangeAdmin(admin.ModelAdmin):
    # Запись
    date_hierarchy = 'date'

    fields = (
        'date',
        'change',
        'event',
        'note',
    )

    inlines = [
        OrgUnitCreationInline,
        OrgUnitAbolitionInline,
    ]

    # Список

    # Вывод форматированного поля даты создания
    def view_list_display_change_date(self, obj):
        if obj.date:
            return obj.date.strftime("%d.%m.%Y")

    view_list_display_change_date.short_description = 'Дата'

    list_display = (
        'view_list_display_change_date',
        'event',
        'change',
    )

    list_display_links = (
        'event',
    )

    list_filter = (
        'date',
        'change',
    )

    search_fields = (
        'event',
        'search_line',
    )

    # Отключить действия
    actions = None


# Вывод подчинённых подразделений
class OrgUnitSubjectsInline(admin.TabularInline):
    model = models.OrgUnit
    fk_name = 'parent'
    fields = (
        'exist',
        'structure_code',
        'short_name',
        'name',
        'date_creation',
        'date_abolition',
    )
    readonly_fields = (
        'exist',
        'structure_code',
        'short_name',
        'name',
        'date_creation',
        'date_abolition',
    )
    ordering = [
        '-exist',
        'name',
    ]
    extra = 0
    verbose_name_plural = 'Подчинённые подразделения'
    can_delete = False
    can_add = False
    show_change_link = True

    def has_add_permission(self, request, obj): return False


# Подразделение
@admin.register(models.OrgUnit)
class OrgUnitAdmin(admin.ModelAdmin):
    # Запись
    fieldsets = (
        ('Параметры подразделения', {
            'fields': (
                'type_of_unit',
                'name',
                'short_name',
                'structure_code',
                'parent',
                'exist',
            )
        }),
        ('Сведения о создании подразделения', {
            'fields': (
                'reason_creation',
                'date_creation',
            )
        }),
        ('Сведения об упразднении подразделения', {
            'fields': (
                'reason_abolition',
                'date_abolition',
            )
        }),
    )

    raw_id_fields = (
        'parent',
        'reason_creation',
        'reason_abolition',
    )

    readonly_fields = (
        'date_creation',
        'date_abolition',
        'exist',
    )

    inlines = [
        OrgUnitSubjectsInline,
    ]

    # Список

    # Вывод форматированного поля даты создания
    def view_list_display_date_creation(self, obj):
        if obj.date_creation:
            return obj.date_creation.strftime("%d.%m.%Y")

    view_list_display_date_creation.empty_value_display = '?'
    view_list_display_date_creation.short_description = 'Дата создания'

    # Вывод форматированного поля даты упразднения
    def view_list_display_date_abolition(self, obj):
        if obj.date_abolition:
            return obj.date_abolition.strftime("%d.%m.%Y")

    view_list_display_date_abolition.empty_value_display = ''
    view_list_display_date_abolition.short_description = 'Дата упразднения'

    list_display = (
        'exist',
        'structure_code',
        'short_name',
        'name',
        'type_of_unit',
        'view_list_display_date_creation',
        'view_list_display_date_abolition',
    )

    list_display_links = (
        'name',
        'short_name',
    )

    list_filter = (
        'exist',
        'type_of_unit',
        'date_creation',
        'date_abolition',
    )

    search_fields = (
        'name',
        'short_name',
        'structure_code',
        'search_line'
    )

    # Отключить действия
    actions = None
