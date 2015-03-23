<%inherit file='base.mako' />

% if errors:
<ul>
    % for e in errors:
        <p class="bg-warning">${ e }</p>
    % endfor
</ul>
% endif
<form method="post" action="${ request.path }">
    <p class="small">Owner: <a href="${ request.route_url('user', login=owner) }">${ owner }</a></p>
    <form>
        <div class="col-md-3">
        <div class="form-group">
            <label>Page Title</label>
            <input class="form-control" type="text" name="title" placeholder="My page title" value="${ title }"/>
        </div>
        <div class="form-group">
            <label>Page Body</label>
            <textarea class="form-control" name="body" rows="5" placeholder="My page content">${ body }</textarea>
        </div>
        <button type="submit" name="submit" value="Submit"/>Submit</button>
    </div>
    </form>
</form>
