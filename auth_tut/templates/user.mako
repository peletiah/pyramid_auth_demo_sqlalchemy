<%inherit file='base.mako' />

<p><a href="${ request.route_url('home') }">Home</a></p>

<h1>User Information</h1>
<p>Login: ${ user.login }</p>
<p>Password: ${ user.password }</p>
<p>Groups:
<ul>
% for group in user.groups:
    <li><a href="${ request.route_url('edit_group', name=group.name, action='edit') }">${ group.name }</a></li>
% endfor 
</ul>
</p>

<p>Pages:<ul>
% for page in pages:
    <li><a href="${ request.route_url('page', title=page.uri) }">${ page.title }</a></li>
% endfor
</ul>
</p>
