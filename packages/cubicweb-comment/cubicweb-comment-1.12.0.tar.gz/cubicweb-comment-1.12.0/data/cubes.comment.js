/*
 *  :organization: Logilab
 *  :copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 *  :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
 */

/* this function is called on inlined-comment editions
 *
 * It calls the [add|eid]_comment method on the jsoncontroller and [re]load
 * only the view for the added or edited comment
 */
function processComment(eid, creation, parentcreated, context) {
    validateForm(
	'commentsForm' + eid, null,
	function(result, formid, cbargs) {
	    var neweid = result[2].eid;
	    if (creation) {
		var $commentNode = $('#comment'+ eid);
		if (!$commentNode.length) {
		    if (parentcreated) {
			// the top level entity has just been created, reload
			// the whole components section
			reloadCtxComponentsSection(context, neweid, eid)
		    } else {
			// only reload the comments component
			reload('commentsection' + eid, 'commentsection',
			       'ctxcomponents', null, eid);
		    }
		    return ;
		}
		var ul = $commentNode.find('> ul:first');
		if (!ul.length) {
		    ul = $(UL({'class': 'section'}));
		    $commentNode.append(ul);
		}
		ul.append(LI({'id': 'comment'+ neweid, 'class': 'comment'},
			     DIV({'id': 'comment'+ neweid + 'Div'})));
		$('#comment' + eid + 'Slot').remove();
	    }
	    var params = ajaxFuncArgs('render', null, 'views', 'treeitem', neweid);
	    $('#comment' + neweid + 'Div').loadxhtml('json', params, null, 'swap', true);
	});
}

function cancelCommentEdition(eid, creation) {
    // comment cancelled, close div holding the form
    $('#comment' + eid + 'Slot').remove();
    // on edition, show back the comment's content
    if (!creation) {
	$('#comment' + eid + 'Div div').show();
    }
}

function showLoginBox() {
    toggleVisibility('popupLoginBox');
    $('html, body').animate({scrollTop:0}, 'fast');
    return false;
}

$(function () {
    $(document).on('click', '.cwjs-comment-reply', function (evt) {
        var $mynode = $(evt.currentTarget),
            $comment = $mynode.closest('.cwjs-comment'),
            eid = $comment.data('eid'),
            $holder = $comment.find('.cwjs-comment-holder'),
            args = ajaxFuncArgs('view', {eid: eid, vid: 'addcommentform'});

        $holder.loadxhtml(AJAX_BASE_URL, args, 'get', 'replace');
        return false;
    });

    $(document).on('click', '.cwjs-comment-edit', function (evt) {
        var $mynode = $(evt.currentTarget),
            $comment = $mynode.closest('.cwjs-comment'),
            eid = $comment.data('eid'),
            args = ajaxFuncArgs('view', {eid: eid, vid: 'editcommentform'});

        $comment.find('.commentBody').hide();
        $comment.loadxhtml(AJAX_BASE_URL, args, 'get', 'append');
        return false;
    });

    $(document).on('click', '.cwjs-comment-delete', function (evt) {
        var $mynode = $(evt.currentTarget),
            $comment = $mynode.closest('.cwjs-comment'),
            eid = $comment.data('eid'),
            redirect = $mynode.data('redirect'),
            args = ajaxFuncArgs('view', {eid: eid, vid: 'deleteconf',
                                         __redirectpath: redirect});

        $comment.find('.commentBody').loadxhtml(AJAX_BASE_URL, args, 'get');
        return false;
    });
});
