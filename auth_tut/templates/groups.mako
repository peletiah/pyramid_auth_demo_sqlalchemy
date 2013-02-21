<%inherit file='base.mako' />

<p><a href="${ request.route_url('home') }">Home</a></p>
<p>Create a page <a href="${ request.route_url('create_group') }">here</a></p>

<h1>All Groups</h1>
% for group in groups:
<p><a href="${ request.route_url('edit_group', name=group.name, action='edit') }">${ group.name }</a></p>
% endfor
