"""PytSite Content Package.
"""
from typing import Callable as _Callable
from datetime import datetime as _datetime
from os import path as _path, makedirs as _makedirs
from pytsite import admin as _admin, taxonomy as _taxonomy, auth as _auth, odm as _odm, util as _util, \
    router as _router, lang as _lang, logger as _logger, feed as _feed, reg as _reg
from . import _model

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


__models = {}


def register_model(model: str, cls, title: str, menu_weight: int=0, icon: str='fa fa-file-text-o', replace=False):
    """Register content model.
    :type cls: str | _odm.Model
    """
    # Resolve class
    if isinstance(cls, str):
        cls = _util.get_class(cls)

    if not issubclass(cls, _model.Content):
        raise TypeError('Subclass of content model expected.')

    if not replace and is_model_registered(model):
        raise KeyError("Model '{}' is already registered.".format(model))

    # Register ODM model
    _odm.register_model(model, cls, replace)

    # Saving info about registered _content_ model
    __models[model] = (cls, title)

    # Define 'bypass_moderation' permission
    perm_name = 'pytsite.content.bypass_moderation.' + model
    perm_description = cls.resolve_partly_msg_id('content_permission_bypass_moderation_' + model)
    _auth.define_permission(perm_name, perm_description, cls.package_name())

    # Define 'set_localization' permission
    perm_name = 'pytsite.content.set_localization.' + model
    perm_description = cls.resolve_partly_msg_id('content_permission_set_localization_' + model)
    _auth.define_permission(perm_name, perm_description, cls.package_name())

    # Define 'set_date' permission
    perm_name = 'pytsite.content.set_publish_time.' + model
    perm_description = cls.resolve_partly_msg_id('content_permission_set_publish_time_' + model)
    _auth.define_permission(perm_name, perm_description, cls.package_name())

    _admin.sidebar.add_menu(
        sid='content',
        mid=model,
        title=title,
        href=_router.ep_url('pytsite.odm_ui.ep.browse', {'model': model}),
        icon=icon,
        weight=menu_weight,
        permissions=(
            'pytsite.odm_ui.browse.' + model,
            'pytsite.odm_ui.browse_own.' + model,
        ),
        replace=replace
    )


def is_model_registered(model: str) -> bool:
    """Check if the content model is registered.
    """
    return model in __models


def get_models() -> dict:
    """Get registered content models.
    """
    return __models


def get_model(model: str) -> tuple:
    """Get model information.
    """
    if not is_model_registered(model):
        raise KeyError("Model '{}' is not registered as content model.".format(model))

    return __models[model]


def get_model_title(model: str) -> str:
    """Get human readable model title.
    """
    return _lang.t(get_model(model)[1])


def dispense(model: str) -> _model.Content:
    """Create content entity.
    """
    if not is_model_registered(model):
        raise KeyError("Model '{}' is not registered as content model.".format(model))

    return _odm.dispense(model)


def find(model: str, status='published', check_publish_time=True, language: str=None):
    """Get content entities finder.
    """
    if not is_model_registered(model):
        raise KeyError("Model '{}' is not registered as content model.".format(model))

    f = _odm.find(model).sort([('publish_time', _odm.I_DESC)])

    if not language:
        language = _lang.get_current()
    f.where('language', '=', language)

    if status:
        f.where('status', '=', status)
    if check_publish_time:
        f.where('publish_time', '<=', _datetime.now())

    return f


def get_publish_statuses() -> list:
    """Get allowed content publication statuses.
    """
    r = []
    for s in ('published', 'waiting', 'unpublished'):
        r.append((s, _lang.t('pytsite.content@status_' + s)))

    return r


def get_sections(language: str=None) -> _odm.FinderResult:
    return list(_taxonomy.find('section', language).sort([('order', _odm.I_ASC)]).get())


def get_section(alias: str, language: str=None) -> _model.Section:
    return _taxonomy.find('section', language).where('alias', '=', alias).first()


def create_section(title: str, alias: str=None, language: str=None) -> _model.Section:
    return _taxonomy.dispense('section', title, alias, language).save()


def get_tags(limit: int=0, language: str=None) -> _odm.FinderResult:
    return _taxonomy.find('tag', language).get(limit)


def get_tag(alias: str, language: str=None) -> _model.Tag:
    return _taxonomy.find('tag', language).where('alias', '=', alias).first()


def create_tag(title: str, alias: str=None, language: str=None) -> _model.Tag:
    return _taxonomy.dispense('tag', title, alias, language).save()


def generate_rss(generator: _feed.rss.Generator, model: str, filename: str, lng: str=None,
                 finder_setup: _Callable[[_odm.Finder], None]=None,
                 item_setup: _Callable[[_feed.rss.Item, _model.Content], None]=None,
                 **kwargs):
    """
    """
    length = kwargs.get('length', 20)

    if not lng:
        lng = _lang.get_current()

    # Setup finder
    finder = find(model, language=lng)
    if finder_setup:
        finder_setup(finder)

    # Preparing output directory
    output_dir = _path.join(_reg.get('paths.static'), 'feed')
    if not _path.exists(output_dir):
        _makedirs(output_dir, 0o755, True)

    for entity in finder.get(length):
        item = generator.dispense_item()
        item.title = entity.title
        item.link = entity.url
        item.description = entity.description if entity.description else entity.title
        item.pub_date = entity.publish_time
        item.author = '{} ({})'.format(entity.author.email, entity.author.full_name)

        if entity.has_field('section'):
            item.add_child(_feed.rss.Category(entity.section.title))
        elif entity.has_field('tags'):
            item.add_child(_feed.rss.Category(entity.tags[0].title))

        if entity.has_field('images'):
            for img in entity.images:
                item.add_child(_feed.rss.Enclosure(img.url, img.length, img.mime))

        if item_setup:
            item_setup(item, entity)

        generator.add_item(item)

    # Write feed content
    out_path = _path.join(output_dir, '{}-{}.xml'.format(filename, lng))
    with open(out_path, 'wt') as f:
        f.write(generator.generate())
    _logger.info("RSS feed successfully written to '{}'.".format(out_path), __name__)
