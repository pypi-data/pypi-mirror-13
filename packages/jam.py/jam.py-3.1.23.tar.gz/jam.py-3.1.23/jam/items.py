# -*- coding: utf-8 -*-

import sys
import logging

import lang.langs as langs
import common

ITEM_INFO = ITEM_ID, ITEM_NAME, ITEM_CAPTION, ITEM_VISIBLE, ITEM_TYPE, ITEM_JS_FILENAME, \
    ITEM_ITEMS, ITEM_FIELDS, ITEM_FILTERS, ITEM_REPORTS = range(10)

class AbortException(Exception):
    pass

class AbstractItem(object):
    def __init__(self, owner, name='', caption='', visible = True, item_type_id=0, js_filename=''):
        self.owner = owner
        self.item_name = name
        self.items = []
        self.ID = None
        self._events = []
        self.master = None
        self.js_filename = js_filename
        if owner:
            if not owner.find(name):
                owner.items.append(self)
                if not hasattr(owner, self.item_name):
                    setattr(owner, self.item_name, self)
            self.task = owner.task
        self.item_caption = caption
        self.visible = visible
        self.item_type_id = item_type_id

    def find(self, name):
        for item in self.items:
            if item.item_name == name:
                return item

    def item_by_ID(self, id_value):
        if self.ID == id_value:
            return self
        for item in self.items:
            result = item.item_by_ID(id_value)
            if result:
                return result

    def write_info(self, info):
        info[ITEM_ID] = self.ID
        info[ITEM_NAME] = self.item_name
        info[ITEM_CAPTION] = self.item_caption
        info[ITEM_VISIBLE] = self.visible
        info[ITEM_TYPE] = self.item_type_id
        info[ITEM_JS_FILENAME] = self.js_filename

    def read_info(self, info):
        self.ID = info[ITEM_ID]
        self.item_name = info[ITEM_NAME]
        self.item_caption = info[ITEM_CAPTION]
        self.visible = info[ITEM_VISIBLE]
        self.item_type_id = info[ITEM_TYPE]
        self.js_filename = info[ITEM_JS_FILENAME]

    def get_info(self):
        result = [None for i in range(len(ITEM_INFO))]
        result[ITEM_ITEMS] = []
        self.write_info(result)
        for item in self.items:
            result[ITEM_ITEMS].append((item.item_type_id, item.get_info()))
        return result

    def get_child_class(self, item_type_id):
        pass

    def set_info(self, info):
        self.read_info(info)
        for item_type_id, item_info in info[ITEM_ITEMS]:
            child = self.get_child_class(item_type_id)(self)
            child.item_type_id = item_type_id
            child.set_info(item_info)

    def bind_item(self):
        pass

    def bind_items(self):
        self.bind_item()
        for item in self.items:
            item.bind_items()
        self.item_type = common.ITEM_TYPES[self.item_type_id - 1]


    def get_module_name(self):
        result = self.owner.get_module_name() + '.' + self.item_name
        return str(result)

    def store_handlers(self):
        result = {}
        for key, value in self.__dict__.items():
            if key[0:3] == 'on_':
                result[key] = self.__dict__[key]
        return result

    def clear_handlers(self):
        for key, value in self.__dict__.items():
            if key[0:3] == 'on_':
                self.__dict__[key] = None

    def load_handlers(self, handlers):
        for key, value in handlers.items():
            self.__dict__[key] = handlers[key]

    def get_master_field(self, fields, master_field):
        for field in fields:
            if field.ID == master_field:
                return field

    def abort(self, message=''):
        message = u'execution aborted: %s %s' % (self.item_name, message)
        raise AbortException, message

    def register(self, func):
        setattr(self, func.__name__, func)



class AbstrGroup(AbstractItem):
    pass


class AbstrTask(AbstractItem):
    def __init__(self, owner, name, caption, visible = True, item_type_id=0, js_filename=''):
        AbstractItem.__init__(self, owner, name, caption, visible, item_type_id, js_filename)
        self.task = self
        self.__language = None
        self.item_type_id = common.TASK_TYPE
        self.log = None

    def set_info(self, info):
        super(AbstrTask, self).set_info(info)
        self.bind_items()

    def item_by_name(self, item_name):
        for group in self.items:
            if group.item_name == item_name:
                return group
            else:
                for item in group.items:
                    if item.item_name == item_name:
                        return item

    def compile_item(self, item):
        pass

    def compile_all(self):
        for module in self.modules:
            del sys.modules[module]
        self.modules = []
        self.compile_item(self)
        for group in self.items:
            self.compile_item(group)
        for group in self.items:
            for item in group.items:
                self.compile_item(item)
        for group in self.items:
            for item in group.items:
                if group.item_type_id != common.REPORTS_TYPE:
                    for detail in item.details:
                        self.compile_item(detail)

    def get_language(self):
        return self.__language

    def set_language(self, value):
        self.__language = value
        self.lang = langs.get_lang_dict(value)
        common.SETTINGS['LAGUAGE'] = value

    language = property (get_language, set_language)

    def get_lang(self):
        return self.lang

    def write_setting(self, connsection):
        pass

    def get_settings(self):
        return common.SETTINGS

    def set_settings(self, value):
        common.SETTINGS = value
        for key in common.SETTINGS.keys():
            common.__dict__[key] = common.SETTINGS[key]
        self.language = common.SETTINGS['LANGUAGE']
        if common.SETTINGS['LOG_FILE'].strip():
            sys.stdout = open(common.SETTINGS['LOG_FILE'].strip(), 'a')
            sys.stderr = open(common.SETTINGS['LOG_FILE'].strip(), 'a')

    def init_locale(self):
        import locale
        result = {}
        try:
            locale.setlocale(locale.LC_ALL, '')
            loc = locale.localeconv()
            for setting in common.LOCALE_SETTINGS:
                try:
                    common.SETTINGS[setting] = loc['setting'.lower()]
                except:
                    common.SETTINGS[setting] = common.DEFAULT_SETTINGS[setting]
        except:
            pass
        try:
            common.SETTINGS['D_FMT'] = locale.nl_langinfo(locale.D_FMT)
        except:
            common.SETTINGS['D_FMT'] = '%Y-%m-%d'
        common.SETTINGS['D_T_FMT'] = '%s %s' % (common.D_FMT, '%H:%M')

class AbstrItem(AbstractItem):
    def __init__(self, owner, name, caption, visible = True, item_type_id=0, js_filename=''):
        AbstractItem.__init__(self, owner, name, caption, visible, item_type_id, js_filename)
        if not hasattr(self.task, self.item_name):
            setattr(self.task, self.item_name, self)

    def write_info(self, info):
        super(AbstrItem, self).write_info(info)
        info[ITEM_FIELDS] = self.field_defs
        info[ITEM_FILTERS] = self.filter_defs
        info[ITEM_REPORTS] = self.get_reports_info()

    def read_info(self, info):
        super(AbstrItem, self).read_info(info)
        self.create_fields(info[ITEM_FIELDS])
        self.create_filters(info[ITEM_FILTERS])
        self.reports = info[ITEM_REPORTS]

    def bind_item(self):
        self.prepare_fields()
        self.prepare_filters()
        self.fields = list(self._fields)


class AbstrDetail(AbstrItem):

    def read_info(self, info):
        super(AbstrDetail, self).read_info(info)
        self.owner.details.append(self)
        if not hasattr(self.owner.details, self.item_name):
            setattr(self.owner.details, self.item_name, self)


class AbstrReport(AbstractItem):
    def __init__(self, owner, name, caption, visible = True, item_type_id=0, js_filename=''):
        AbstractItem.__init__(self, owner, name, caption, visible, item_type_id, js_filename)
        if not hasattr(self.task, self.item_name):
            setattr(self.task, self.item_name, self)

    def write_info(self, info):
        super(AbstrReport, self).write_info(info)
        info[ITEM_FIELDS] = self.param_defs

    def read_info(self, info):
        super(AbstrReport, self).read_info(info)
        self.create_params(info[ITEM_FIELDS])

    def param_by_name(self, name):
        for param in self.params:
            if param.param_name == name:
                return param

    def bind_item(self):
        self.prepare_params()

