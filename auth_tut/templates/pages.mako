<%inherit file='base.mako' />

<p><a href="${ request.route_url('home') }">Home</a></p>
<hr>
<p>Create a page <a href="${ request.route_url('create_page') }">here</a></p>
<hr>

<h4>Existing Pages:</h4>
% for page in pages:
<p><a href="${ request.route_url('page', title=page.uri) }">${ page.title }</a></p>
% endfor
