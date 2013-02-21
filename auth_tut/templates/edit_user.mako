<%inherit file='base.mako' />

% if errors:
<ul>
    % for e in errors:
    <li>${ e }</li>
    % endfor
</ul>
% endif
<form method="post" action="${ request.path }">
    <h3>Login</h3>
    <input type="text" name="login" value="${ login }"/>
    <h3>Password</h3>
    <input type="password" name="password" value="${ password }"/>
    <p>
    <input type="submit" name="submit" value="Submit"/></p>
</form>
