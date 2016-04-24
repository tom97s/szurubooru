import datetime
import pytest
from szurubooru import api, db, errors
from szurubooru.func import util, comments

@pytest.fixture
def test_ctx(config_injector, context_factory, user_factory, comment_factory):
    config_injector({
        'ranks': ['anonymous', 'regular_user', 'mod'],
        'rank_names': {'anonymous': 'Peasant', 'regular_user': 'Lord', 'mod': 'King'},
        'privileges': {
            'comments:edit:self': 'regular_user',
            'comments:edit:any': 'mod',
        },
        'thumbnails': {'avatar_width': 200},
    })
    db.session.flush()
    ret = util.dotdict()
    ret.context_factory = context_factory
    ret.user_factory = user_factory
    ret.comment_factory = comment_factory
    ret.api = api.CommentDetailApi()
    return ret

def test_simple_updating(test_ctx, fake_datetime):
    user = test_ctx.user_factory(rank='regular_user')
    comment = test_ctx.comment_factory(user=user)
    db.session.add(comment)
    db.session.commit()
    with fake_datetime('1997-12-01'):
        result = test_ctx.api.put(
            test_ctx.context_factory(input={'text': 'new text'}, user=user),
            comment.comment_id)
    assert result['comment']['text'] == 'new text'
    comment = db.session.query(db.Comment).one()
    assert comment is not None
    assert comment.text == 'new text'
    assert comment.last_edit_time is not None

@pytest.mark.parametrize('input,expected_exception', [
    ({'text': None}, comments.EmptyCommentTextError),
    ({'text': ''}, comments.EmptyCommentTextError),
    ({'text': []}, comments.EmptyCommentTextError),
    ({'text': [None]}, errors.ValidationError),
    ({'text': ['']}, comments.EmptyCommentTextError),
])
def test_trying_to_pass_invalid_input(test_ctx, input, expected_exception):
    user = test_ctx.user_factory()
    comment = test_ctx.comment_factory(user=user)
    db.session.add(comment)
    db.session.commit()
    with pytest.raises(expected_exception):
        test_ctx.api.put(
            test_ctx.context_factory(input=input, user=user),
            comment.comment_id)

def test_trying_to_omit_mandatory_field(test_ctx):
    user = test_ctx.user_factory()
    comment = test_ctx.comment_factory(user=user)
    db.session.add(comment)
    db.session.commit()
    with pytest.raises(errors.ValidationError):
        test_ctx.api.put(
            test_ctx.context_factory(input={}, user=user),
            comment.comment_id)

def test_trying_to_update_non_existing(test_ctx):
    with pytest.raises(comments.CommentNotFoundError):
        test_ctx.api.put(
            test_ctx.context_factory(
                input={'text': 'new text'},
                user=test_ctx.user_factory(rank='regular_user')),
            5)

def test_trying_to_update_someones_comment_without_privileges(test_ctx):
    user = test_ctx.user_factory(rank='regular_user')
    user2 = test_ctx.user_factory(rank='regular_user')
    comment = test_ctx.comment_factory(user=user)
    db.session.add(comment)
    db.session.commit()
    with pytest.raises(errors.AuthError):
        test_ctx.api.put(
            test_ctx.context_factory(input={'text': 'new text'}, user=user2),
            comment.comment_id)

def test_updating_someones_comment_with_privileges(test_ctx):
    user = test_ctx.user_factory(rank='regular_user')
    user2 = test_ctx.user_factory(rank='mod')
    comment = test_ctx.comment_factory(user=user)
    db.session.add(comment)
    db.session.commit()
    try:
        test_ctx.api.put(
            test_ctx.context_factory(input={'text': 'new text'}, user=user2),
            comment.comment_id)
    except:
        pytest.fail()