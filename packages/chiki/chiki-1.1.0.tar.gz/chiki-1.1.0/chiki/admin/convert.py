# coding: utf-8
from flask.ext.admin import form
from flask.ext.admin.contrib.mongoengine.form import CustomModelConverter
from flask.ext.admin.model.fields import AjaxSelectField, AjaxSelectMultipleField
from flask.ext.mongoengine.wtf import orm, fields as mongo_fields
from mongoengine import ReferenceField
from ..forms.fields import FileField, ImageField, AreaField, ListField
from ..forms.fields import ModelSelectMultipleField


class KModelConverter(CustomModelConverter):

    @orm.converts('XFileField')
    def conv_kfile(self, model, field, kwargs):
        return FileField(max_size=field.max_size, allows=field.allows, **kwargs)

    @orm.converts('XImageField')
    def conv_kimage(self, model, field, kwargs):
        return ImageField(max_size=field.max_size, allows=field.allows, **kwargs)

    @orm.converts('AreaField')
    def conv_area(self, model, field, kwargs):
        return AreaField(**kwargs)

    @orm.converts('ListField')
    def conv_list(self, model, field, kwargs):
        if field.field is None:
            raise ValueError('ListField "%s" must have field specified for model %s' % (field.name, model))

        if isinstance(field.field, ReferenceField):
            loader = getattr(self.view, '_form_ajax_refs', {}).get(field.name)
            if loader:
                return AjaxSelectMultipleField(loader, **kwargs)

            kwargs['widget'] = form.Select2Widget(multiple=True)

            doc_type = field.field.document_type
            return ModelSelectMultipleField(model=doc_type, **kwargs)

        # Create converter
        view = self._get_subdocument_config(field.name)
        converter = self.clone_converter(view)

        if field.field.choices:
            kwargs['multiple'] = True
            return converter.convert(model, field.field, kwargs)

        unbound_field = converter.convert(model, field.field, {})
        return ListField(unbound_field, min_entries=0, **kwargs)

    @orm.converts('XListField')
    def conv_xlist(self, model, field, kwargs):
        if field.field is None:
            raise ValueError('ListField "%s" must have field specified for model %s' % (field.name, model))

        if isinstance(field.field, ReferenceField):
            loader = getattr(self.view, '_form_ajax_refs', {}).get(field.name)
            if loader:
                return AjaxSelectMultipleField(loader, **kwargs)

            kwargs['widget'] = form.Select2Widget(multiple=True)

            doc_type = field.field.document_type
            return ModelSelectMultipleField(model=doc_type, **kwargs)

        # Create converter
        view = self._get_subdocument_config(field.name)
        converter = self.clone_converter(view)

        if field.field.choices:
            kwargs['multiple'] = True
            return converter.convert(model, field.field, kwargs)

        unbound_field = converter.convert(model, field.field, {})
        return ListField(unbound_field, min_entries=0, **kwargs)