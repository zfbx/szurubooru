import datetime
import pytest
from szurubooru import api, db, errors
from szurubooru.func import misc, tag_categories

@pytest.fixture
def test_ctx(
        context_factory, config_injector, user_factory, tag_category_factory):
    config_injector({
        'privileges': {
            'tag_categories:list': 'regular_user',
            'tag_categories:view': 'regular_user',
        },
        'thumbnails': {'avatar_width': 200},
        'ranks': ['anonymous', 'regular_user', 'mod', 'admin'],
        'rank_names': {'regular_user': 'Peasant'},
    })
    ret = misc.dotdict()
    ret.context_factory = context_factory
    ret.user_factory = user_factory
    ret.tag_category_factory = tag_category_factory
    ret.list_api = api.TagCategoryListApi()
    ret.detail_api = api.TagCategoryDetailApi()
    return ret

def test_retrieving_multiple(test_ctx):
    db.session.add_all([
        test_ctx.tag_category_factory(name='c1'),
        test_ctx.tag_category_factory(name='c2'),
    ])
    result = test_ctx.list_api.get(
        test_ctx.context_factory(
            user=test_ctx.user_factory(rank='regular_user')))
    assert [cat['name'] for cat in result['tagCategories']] == ['c1', 'c2']

def test_retrieving_single(test_ctx):
    db.session.add(test_ctx.tag_category_factory(name='cat'))
    result = test_ctx.detail_api.get(
        test_ctx.context_factory(
            user=test_ctx.user_factory(rank='regular_user')),
        'cat')
    assert result == {
        'tagCategory': {
            'name': 'cat',
            'color': 'dummy',
        },
        'snapshots': [],
    }

def test_trying_to_retrieve_single_non_existing(test_ctx):
    with pytest.raises(tag_categories.TagCategoryNotFoundError):
        test_ctx.detail_api.get(
            test_ctx.context_factory(
                user=test_ctx.user_factory(rank='regular_user')),
            '-')

def test_trying_to_retrieve_single_without_privileges(test_ctx):
    with pytest.raises(errors.AuthError):
        test_ctx.detail_api.get(
            test_ctx.context_factory(
                user=test_ctx.user_factory(rank='anonymous')),
            '-')