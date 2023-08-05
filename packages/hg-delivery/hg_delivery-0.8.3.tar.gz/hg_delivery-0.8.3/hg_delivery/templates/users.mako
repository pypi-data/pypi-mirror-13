<%!
  import json
  import os.path
%>
<%inherit file="base.mako"/>
<%namespace name="lib" file="lib.mako"/>
  <h2>
        <span class="label label-default">User management</span>
        <button style="background-color:transparent;border:none" onclick="$('#new_user_dialog').modal('show');" alt="add a user">
          <span class='glyphicon glyphicon-plus' style="font-size:26px;vertical-align:bottom"></span>
        </button>
  </h2>

  <div id="overview" class="panel panel-default">
    <div>
       <p class="bg-info" style="padding:5px">
         Your list of users
       </p>
    </div>
    <div>
       <!-- project compare table -->
       <table id="users_overview" class="table table-condensed" data-update_url="${url('users_json')}">
          <thead>
            <th>Name</th>
            <th>Email (a.k.a. login)</th>
            <th>Creation date</th>
            <th>Action</th>
            <th>Action</th>
          </thead>
          <tbody>
            % for user in lst_users :
               <tr>
                  <td>${user.name}</td>
                  <td>${user.email}</td>
                  <td>${user.creation_date.strftime('%d/%m/%Y %H:%M')}</td>
                  <td><button class="btn btn-default" onclick="edit_user('${url('user_update', id=user.id)}', '${url('user_get', id=user.id)}', '${user.id}')">edit</button></td>
                  <td><button class="btn btn-default" onclick="delete_user(this,'${url('user_delete', id=user.id)}')">delete</button></td>
               </tr>
            % endfor
            % if not lst_users :
               <tr>
                  <td colspan="5" style="text-align:center;padding-top:20px">No Users defined</td>
               </tr>
            % endif :
          </tbody>
       </table>
    </div>
  </div>

${lib.publish_user_dialog()}
${lib.publish_update_user_dialog()}

