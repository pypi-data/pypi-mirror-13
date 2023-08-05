<%def name="publish_project_dialog()">
  <div id="new_project_dialog" class="modal">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h4 class="modal-title">Add a new project</h4>
        </div>
        <div class="modal-body">
          <form id="project_add" name="project_add" action="${url('project_add')}" method="post" class="form-horizontal" role="form">
            <div id="new_project">
                <div class="form-group">
                  <label for="new_project_name" class="col-sm-2 control-label">Name</label>
                  <div class="col-sm-8">
                    <input id="new_project_name" class="form-control" name="name" type="text" placeholder="name">
                  </div>
                </div>
                <div class="form-group">
                  <label for="new_project_host" class="col-sm-2 control-label">Host</label>
                  <div class="col-sm-8">
                    <input id="new_project_host" class="form-control" name="host" type="text" placeholder="hostname">
                  </div>
                </div>
                <div class="form-group">
                  <label for="new_project_path" class="col-sm-2 control-label">Folder</label>
                  <div class="col-sm-8">
                    <input id="new_project_path" class="form-control" name="path" type="text" placeholder="/home/sites ...">
                  </div>
                </div>
                <div class="form-group">
                  <label for="new_project_user" class="col-sm-2 control-label">User</label>
                  <div class="col-sm-8">
                    <input id="new_project_user" class="form-control" name="user" type="text" placeholder="user">
                  </div>
                </div>
                <div class="form-group">
                  <label for="new_project_password" class="col-sm-2 control-label">Passwd</label>
                  <div class="col-sm-8">
                    <input id="new_project_password" class="form-control" name="password" type="password" placeholder="password">
                    <input name="dashboard" type="hidden" value="0">
                    <input name="rev_init" type="hidden" value="0">
                    <input name="dvcs_release" type="hidden" value="">
                  </div>
                </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button id="cancel_add_project" type="button" class="btn btn-default" data-dismiss="modal">Close</button>
          <button id="add_my_project" type="button" class="btn btn-primary" onclick="add_project('${url('project_add')}');">Save changes</button>
        </div>
      </div><!-- /.modal-content -->
    </div><!-- /.modal-dialog -->
  </div><!-- /.modal -->
</%def>


<%def name="publish_user_dialog()">
<div id="new_user_dialog" class="modal">
  <div class="modal-dialog">
    <div class="modal-content">

      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title">Add a new user</h4>
      </div><!-- /.modal-header -->

      <div class="modal-body">
        <form id="user" name="user" action="${url('user_add')}" method="post" class="form-horizontal" role="form">
          <div id="new_user">
              <div class="form-group">
                <label for="new_user_name" class="col-sm-2 control-label">Full name</label>
                <div class="col-sm-8">
                  <input id="new_user_name" class="form-control" name="name" type="text" placeholder="name">
                </div>
              </div>
              <div class="form-group">
                <label for="new_user_name" class="col-sm-2 control-label">Email</label>
                <div class="col-sm-8">
                  <input id="new_user_email" class="form-control" name="email" type="text" placeholder="email">
                </div>
              </div>
              <div class="form-group">
                <label for="new_user_password" class="col-sm-2 control-label">Passwd</label>
                <div class="col-sm-8">
                  <input id="new_user_password" class="form-control" name="pwd" type="password" placeholder="password">
                </div>
              </div>
          </div>
        </form>
      </div><!-- /.modal-body -->

      <div class="modal-footer">
        <button id="cancel_add_user" type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        <button id="add_my_user" type="button" class="btn btn-primary" onclick="add_user('${url('user_add')}');">Save changes</button>
      </div><!-- /.modal-footer -->

    </div><!-- /.modal-content -->
  </div><!-- /.modal-dialog -->
</div><!-- /.modal -->
</%def>

<%def name="publish_update_user_dialog()">
<div id="update_user_dialog" class="modal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title">Update user</h4>
      </div>
      <div class="modal-body">
        <form id="update_user_form" name="user" action="" method="post" class="form-horizontal" role="form">
          <div id="update_user">
              <div class="form-group">
                <label for="udate_user_name" class="col-sm-2 control-label">Full name</label>
                <div class="col-sm-8">
                  <input id="update_user_name" class="form-control" name="name" type="text" placeholder="name">
                </div>
              </div>
              <div class="form-group">
                <label for="update_user_name" class="col-sm-2 control-label">Email</label>
                <div class="col-sm-8">
                  <input id="update_user_email" class="form-control" name="email" type="text" placeholder="email">
                </div>
              </div>
              <div class="form-group">
                <label for="update_user_password" class="col-sm-2 control-label">Passwd</label>
                <div class="col-sm-8">
                  <input id="update_user_password" class="form-control" name="pwd" type="password" placeholder="password">
                </div>
              </div>
          </div>
        </form>
      </div>
      <div class="modal-footer">
        <button id="cancel_update_user" type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        <button id="update_my_user" type="button" class="btn btn-primary">Save changes</button>
      </div>
    </div><!-- /.modal-content -->
  </div><!-- /.modal-dialog -->
</div><!-- /.modal -->
</%def>
