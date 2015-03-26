<%inherit file='base.mako' />

<div class="col-md-3">
% if errors:
    % for e in errors:
        <p class="bg-danger">${e}</p>
    % endfor
% endif

<form method="post" action="${ request.path }">
    <div class="form-group">
        <label>Group Name</label>
        <input type="text" class="form-control" placeholder="enter group name" name='name' value="${ name }"/>
    </div>
% for user in users:
    <%
    check = '' 
    if user.login in member_list:
        check='checked'
    %>
    <div class="form-group">
        <label>
            <input type="checkbox" value="${ user.login }" name="member" ${ check }> ${ user.login }
        </label>
    </div>
% endfor
    <div class="form-group">
        <button type="submit" class="btn btn-primary">Submit</button>
    </div>

</form>
</div>
