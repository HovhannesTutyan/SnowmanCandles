from django.apps import AppConfig


class LanguagesConfig(AppConfig):
    name = "languages"
    verbose_name = "Languages"

    def ready(self):
        # django-modeltranslation copies a field's default into every language column, so a
        # new row would get the English default text as its "Armenian" and "Russian" text.
        # Translations start empty instead (the site shows English until they're filled).
        from modeltranslation.translator import translator

        from .conf import TARGETS, localized, translated_fields

        for model in translator.get_registered_models(abstract=False):
            for field in translated_fields(model):
                for lang in TARGETS:
                    column = model._meta.get_field(localized(field, lang))
                    if isinstance(column.default, str) and column.default:
                        column.default = ""
