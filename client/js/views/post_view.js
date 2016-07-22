'use strict';

const router = require('../router.js');
const views = require('../util/views.js');
const keyboard = require('../util/keyboard.js');
const PostContentControl = require('../controls/post_content_control.js');
const PostNotesOverlayControl =
    require('../controls/post_notes_overlay_control.js');
const PostReadonlySidebarControl =
    require('../controls/post_readonly_sidebar_control.js');
const PostEditSidebarControl =
    require('../controls/post_edit_sidebar_control.js');
const CommentListControl = require('../controls/comment_list_control.js');
const CommentFormControl = require('../controls/comment_form_control.js');

const template = views.getTemplate('post');

class PostView {
    constructor(ctx) {
        this._hostNode = document.getElementById('content-holder');

        const sourceNode = template(ctx);
        const postContainerNode = sourceNode.querySelector('.post-container');
        const sidebarNode = sourceNode.querySelector('.sidebar');
        views.replaceContent(this._hostNode, sourceNode);
        views.syncScrollPosition();

        const postViewNode = document.body.querySelector('.content-wrapper');
        const topNavigationNode =
            document.body.querySelector('#top-navigation');

        const margin = (
            postViewNode.getBoundingClientRect().top -
            topNavigationNode.getBoundingClientRect().height);

        this._postContentControl = new PostContentControl(
            postContainerNode,
            ctx.post,
            () => {
                return [
                    window.innerWidth -
                        postContainerNode.getBoundingClientRect().left -
                        margin,
                    window.innerHeight -
                        topNavigationNode.getBoundingClientRect().height -
                        margin * 2,
                ];
            });

        this._postNotesOverlayControl = new PostNotesOverlayControl(
            postContainerNode.querySelector('.post-overlay'),
            ctx.post);

        this._installSidebar(ctx);
        this._installCommentForm();
        this._installComments(ctx.post.comments);

        keyboard.bind('e', () => {
            if (ctx.editMode) {
                router.show('/post/' + ctx.post.id);
            } else {
                router.show('/post/' + ctx.post.id + '/edit');
            }
        });
        keyboard.bind(['a', 'left'], () => {
            if (ctx.nextPostId) {
                router.show('/post/' + ctx.nextPostId);
            }
        });
        keyboard.bind(['d', 'right'], () => {
            if (ctx.prevPostId) {
                router.show('/post/' + ctx.prevPostId);
            }
        });
    }

    _installSidebar(ctx) {
        const sidebarContainerNode = document.querySelector(
            '#content-holder .sidebar-container');

        if (ctx.editMode) {
            this.sidebarControl = new PostEditSidebarControl(
                sidebarContainerNode,
                ctx.post,
                this._postContentControl,
                this._postNotesOverlayControl);
        } else {
            this.sidebarControl = new PostReadonlySidebarControl(
                sidebarContainerNode, ctx.post, this._postContentControl);
        }
    }

    _installCommentForm() {
        const commentFormContainer = document.querySelector(
            '#content-holder .comment-form-container');
        if (!commentFormContainer) {
            return;
        }

        this.commentFormControl = new CommentFormControl(
            commentFormContainer, null, false, 150);
        this.commentFormControl.enterEditMode();
    }

    _installComments(comments) {
        const commentsContainerNode = document.querySelector(
            '#content-holder .comments-container');
        if (!commentsContainerNode) {
            return;
        }

        this.commentListControl = new CommentListControl(
            commentsContainerNode, comments);
    }
}

module.exports = PostView;
