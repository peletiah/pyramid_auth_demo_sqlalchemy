<%inherit file='base.mako' />

${ request.host }

% if failed_attempt:
    <p class="bg-danger">Invalid credentials, try again.</p>
% endif
<form method="post" action="${ request.path }">
    <p>
        <label for="login">Login</label><br>
        <input type="text" name="login" value="${ login }">
    </p>
    <p>
        <label for="passwd">Password</label><br>
        <input type="password" name="passwd">
    </p>
    <input type="hidden" name="next" value="${ next }">
    <input type="submit" name="submit">
</form>

<h3>Valid combinations in the default database:</h3>
<p>"admin",  password: "admin"</p>
<p>"editor",  password: "editor"</p>
<p>"luser",  password: "luser"</p>

