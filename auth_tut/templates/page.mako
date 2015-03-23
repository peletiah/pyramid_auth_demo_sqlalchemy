<%inherit file='base.mako' />

<p><a href="${ request.route_url('home') }">Home</a></p>
<hr>
<p>Click <a href="${ request.route_url('edit_page', title=page.uri) }">here</a> to edit this page.</p>
<hr>

<h4>${ page.title }</h4>
<p><small>Owner: <a href="${ request.route_url('user', login=user.login) }">${ user.login }</a></small></p>
<p><small>Body:</small></p>
<div style="margin-left: 2em;">
    ${ page.body | n }
</div>
