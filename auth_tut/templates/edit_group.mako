<%inherit file='base.mako' />

% if errors:
<ul>
    % for e in errors:
    <li>${ e }</li>
    % endfor
</ul>
% endif
<form method="post" action="${ request.path }">
    <h3>Group Name</h3>
    <input type="text" name="name" value="${ name }"/>
    <input type="submit" name="submit" value="Submit"/>
% for user in users:
    <%
    check = '' 
    if user.login in members_db:
        check='checked'
    %>
<p><input type="checkbox" name="member" value="${ user.login }" ${ check }>${ user.login }</input></p>
% endfor
</form>
