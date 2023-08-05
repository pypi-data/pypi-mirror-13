<%!
  import json
%>
<%inherit file="base.mako"/>
<%namespace name="lib" file="lib.mako"/>

<%def name="publish_project_html(current_node, filter_branch, filter_tag, last_hundred_change_list)">
    % if current_node is not UNDEFINED and current_node is not None :
      <div class="panel panel-default col-md-6" style="padding-left:0px;padding-right:0px;">
        <div class="panel-heading">
          <h3 class="panel-title">
             project <b>${project.name}</b> position @revision : <i>${current_node.get('rev','UNKNOWN')}</i>
             %if len(linked_projects)==0 :
               <i style="color:red;display:block-inline;padding-left:2em;">This project has no sibling</i>
             %endif
          </h3>
        </div>
        <div class="panel-body">
            <span class="label label-warning"> ${current_node.get('branch','UNKNOWN')}</span>
            <span class="overflow">${current_node.get('node','UNKNOWN')} (using mercurial : ${project.dvcs_release})</span>
            <br><i>(${current_node.get('desc','UNKNOWN')})</i>
        </div>
      </div>
    % endif
    
     <div id="filter" class="panel panel-default col-md-5">
       <div class="panel-heading">
         <h3 class="panel-title">Filter</h3>
       </div>
       <div style="padding:8px 9px">
         <form id="time" name="time" action="" method="POST" role="form" class="form-inline">
           <div class="btn-group">
             <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" style="min-width:80px">
               %if filter_tag :
                 <span id="tag_name">${[t[0] for t in list_tags if t[1]==filter_tag][0]}</span> <span class="caret"></span>
               %else :
                 Tags <span class="caret"></span>
               %endif
             </button>
             <ul class="dropdown-menu" role="menu">
             %if filter_tag :
               <li><a href="#" onclick="$('#tag').val('');$('#time').submit()"><b>All tags</b></a></li>
             %endif
             %for _tag in list_tags :
               <li><a href="#" onclick="$('#tag').val('${_tag[1]}');$('#time').submit()">${_tag[0]}</a></li>
             %endfor
             </ul>
           </div>
           <div class="btn-group">
             <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" style="min-width:80px">
               %if filter_branch :
                 <span id="branch_name">${filter_branch}</span> <span class="caret"></span>
               %else :
                 All branches <span class="caret"></span>
               %endif
             </button>
             <ul class="dropdown-menu" role="menu">
             %if filter_branch :
               <li><a href="#" onclick="$('#branch').val('');$('#time').submit()"><b>All branches</b></a></li>
             %endif
             %for _branch in list_branches :
               <li><a href="#" onclick="$('#branch').val('${_branch}');$('#time').submit()">${_branch}</a></li>
             %endfor
             </ul>
           </div>
           <input type="hidden" id="branch" name="branch" value="">
           <input type="hidden" id="tag" name="tag" value="">
           <input type="text" name="limit" value="${limit}" size="3" maxlength="4" style="margin-left:20px;">
           <button id="view_time_project" class="btn btn-primary" style="float:right">Filter this view</button>
         </form>
       </div>
     </div>
     <div id="d3_container"></div>
</%def>

<ul id="project_tab" class="nav nav-tabs" style="margin-top:4px;margin-bottom:6px">
  <li class="active"> <a href="#project_home">project <b>${project.name}</b></a> </li>
  <li> <a href="#related">Related projects</a> </li>
  <li> <a href="#revision">Revision</a> </li>
  % if allow_to_modify_acls :
    <li> <a href="#users">Users (rights management)</a></li>
  % endif
  % if request.acl_container.contains('edit') :
    <li> <a href="#tasks">Additional Tasks</a> </li>
  % endif
</ul>

<!-- Tab panes -->
<div class="tab-content">

  <!-- a tab -->
  <div class="tab-pane active" id="project_home">
    ${publish_project_html(current_node, filter_branch, filter_tag, last_hundred_change_list)}
  </div>

  <!-- a tab -->
  <div class="tab-pane" id="related">

      <div class="panel panel-default col-md-3" style="padding-left:0px;padding-right:0px;">
        <div class="panel-heading">
          <h3 class="panel-title">Related projects</h3>
        </div>
        <div class="panel-body">
           <div id="other_projects" class="list-group">
             %if len(linked_projects)>0 :
                 %for link in linked_projects :
                 <a href="#" class="list-group-item" data-id="${link.id}" data-pushtest="${url(route_name='project_push_test', id=project.id, target=link.id)}" data-pulltest="${url(route_name='project_pull_test', id=project.id, source=link.id)}" data-url="${url(route_name='project_fetch',id=link.id, source=project.id)}" data-name="${link.name}" onclick="fetch_this_other_project(this)">${link.name}</a>
                 %endfor
             %else :
                 No linked project detected
             %endif
           </div>
        </div>
      </div>

      <div id="pushpull" class="panel panel-default col-md-4" style="margin-left:20px;padding-left:0px;padding-right:0px;display:none">
        <div class="panel-heading">
          <h3 class="panel-title">Should we pull/push from this related project ?</h3>
        </div>
        <div class="panel-body">
           <div id="nosync" style="display:none">
               nothing to synchronize ...
           </div>
           <div id="pushpull_buttons" class="list-group">
             <button id="button_push" disabled="disabled" class="btn btn-primary has-spinner" onclick="push_to(${project.id}, '${url(route_name='project_push_to', id=project.id, target='')}',false);">
               <span class="spinner"><i class="icon-spin glyphicon glyphicon-refresh"></i></span>
               push to
             </button>
             <button id="button_pull" disabled="disabled" class="btn btn-primary has-spinner" onclick="pull_from(${project.id}, '${url(route_name='project_pull_from', id=project.id, source='')}');">
               <span class="spinner"><i class="icon-spin glyphicon glyphicon-refresh"></i></span>
               pull from
             </button>
           </div>
        </div>
      </div>

     <div id="table_project_container">
       <br>
       <!-- project compare table -->
       <table id="project_comparison" class="table table-condensed" style="display:none">
          <thead>
            <th></th>
            <th>Rev <span id="p_name_remote"></span></th>
            <th>Rev <span id="p_name_local"></span></th>
            <th></th>
            <th>Author</th>
            <th>Branch</th>
            <th>Other branch</th>
            <th>Date</th>
            <th>Description</th>
          </thead>
          <tbody>
          </tbody>
       </table>
     </div>

  </div>

  <!-- project revision tab pane -->
  <div class="tab-pane" id="revision">

      <div id="files_panel" class="panel panel-default col-md-5 col-lg-3">
        <div class="panel-heading">
          <h3 class="panel-title">Description and files</h3>
        </div>
        <div class="panel-body">
           <div id="revision_description" class="list-group">
           </div>
           <div id="files" class="list-group">
           </div>
        </div>
      </div>

      <!-- panel who will contains diffs -->
      <div class="panel col-md-5 col-lg-8 col-xs-8" id="diffs_container" style="display:none" data-orig1="${url(route_name='view_file_content', id=project.id,rev="--REV--",file_name="--FNAME--")}" data-orig2="${url(route_name='view_file_content', id=project.id,rev="--REV--",file_name="--FNAME--")}"></div>
      <!-- panel who will contains diffs -->
      
      <!-- if not diff are available -->
      <div class="panel" id="no_diff" style="display:none">
        <p class="bg-info"> <br> &nbsp;  No diff is available for this revision <br> <br></p>
      </div>
      <!-- if not diff are available -->


      <!-- diff merge -->
      <div id="merge_container" style="display:none" class="panel">
      </div>

  </div>

  % if allow_to_modify_acls :
    <!-- project users tab pane -->
    <div class="tab-pane" id="users">
        <div id="files_panel">
          <div class="panel-heading">
            <h3 class="panel-title">What users can do in this project</h3>
          </div>
          <div class="panel-body">
             <form name="project_acls" id="project_acls" action="${url(route_name='project_save_acls', id=project.id)}">
               <table style="width:300px" class="table table-condensed">
                   <thead>
                      <th>User</th>
                      <th>Available roles</th>
                   </thead>
                   <tbody>
                     % for user in users :
                        <tr>
                          <td>${user.name}</td>
                          <td>
                             <select name="projectacl_${user.id}">
                               <option value=""> ----- </option>
                               % for acl_label in knonwn_acl :
                                   % if project_acls.get(user.id) == acl_label :
                                     <option value="${acl_label}" selected>${acl_label}</option>
                                   % else :
                                     <option value="${acl_label}">${acl_label}</option>
                                   % endif
                               % endfor
                             </select>
                          </td>
                        </tr>
                     % endfor 
                   </tbody>
               </table>

               <button type="button" onclick="save_project_acls()" class="btn btn-primary">save modifications</button>
             </form>
          </div>
        </div>
    </div>
  % endif

  % if request.acl_container.contains('edit') :
    <!-- project tasks tab pane -->
    <div class="tab-pane" id="tasks">
        <div id="files_panel">
          <div class="panel-heading">
            <h3 class="panel-title">Additional tasks executed after each update</h3>
          </div>
          <div class="panel-body">

             <form name="project_tasks" id="project_tasks" action="${url(route_name='project_save_tasks', id=project.id)}">
               <ul id="tasks_list">
                   %for task in project_tasks :
                     <li>
                          <input type="text" name="task_content" value="${task.content}">
                          <button data-id="${task.id}" data-url="${url(route_name='project_delete_task', id=task.id)}" onclick="delete_this_task(this)" type="button" class="btn">delete it ..</button>
                          <button data-id="${task.id}" data-url="${url(route_name='project_run_task', id=task.id)}" onclick="run_this_task(this)" type="button" class="btn">run it ..</button>
                     </li>
                   %endfor
               </ul>
               <button type="button" onclick="add_new_task()" class="btn btn-primary">add a task</button>
               <button id="save_tasks" type="button" onclick="save_project_tasks()" class="btn btn-primary">save modifications</button>
             </form>
          </div>
        </div>
    </div>
  % endif
</div>


<!-- project edition -->
<div id="edit_project_dialog" class="modal">
  <div class="modal-dialog">
    <div class="modal-content">

      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title">Add a new project</h4>
      </div>

      <div class="modal-body">
        <div id="edit_project">
           <form id="project" name="project" action="${url(route_name='project_update',id=project.id)}" method="post" class="form-horizontal" role="form">
              <div class="form-group">
                <label for="project_name" class="col-sm-4 control-label">Name</label>
                <div class="col-sm-7">
                  <input id="project_name" class="form-control" name="name" type="text" placeholder="name" value="${project.name}">
                </div>
              </div>
              <div class="form-group">
                <label for="project_host" class="col-sm-4 control-label">Host</label>
                <div class="col-sm-7">
                  <input id="project_host" class="form-control" name="host" type="text" placeholder="hostname" value="${project.host}">
                </div>
              </div>
              <div class="form-group">
                <label for="project_path" class="col-sm-4 control-label">Folder</label>
                <div class="col-sm-7">
                  <input id="project_path" class="form-control" name="path" type="text" placeholder="/home/sites ..." value="${project.path}">
                </div>
              </div>
              <div class="form-group">
                <label for="project_user" class="col-sm-4 control-label">User</label>
                <div class="col-sm-7">
                  <input id="project_user" class="form-control" name="user" type="text" placeholder="user" value="${project.user}">
                </div>
              </div>
              <div class="form-group">
                <label for="project_password" class="col-sm-4 control-label">Passwd</label>
                <div class="col-sm-7">
                  <input id="project_password" class="form-control" name="password" type="password" placeholder="password" value="${project.password}">
                </div>
              </div>
              <div class="form-group">
                <label for="project_dashboard" class="col-sm-4 control-label">Clip to dashboard</label>
                <div class="col-sm-7">
                  <div class="checkbox">
                    <label>
                      % if project.dashboard :
                        <input id="project_dashboard" name="dashboard" type="checkbox" value="1" checked>
                      % else :
                        <input id="project_dashboard" name="dashboard" type="checkbox" value="1">
                      % endif
                    </label>
                  </div>
                </div>
              </div>
           </form>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        <button type="button" class="btn btn-primary" onclick="update_project('${url('project_update', id=project.id)}');">Save changes</button>
      </div>

    </div><!-- /.modal-content -->
  </div><!-- /.modal-dialog -->
</div><!-- /.modal -->
<!-- end of project edition -->

<!-- start update to dialog -->
<div id="confirm_move_dialog" class="modal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title">Are you sure to move project <b>${project.name}</b> ?</h4>
      </div>
      <div class="modal-body">
        <p>
          from <span id="src_revision"></span> to <span id="target_revision"></span> revision
        </p>
        <div id="possible_update" class="list-group">
          <p>
            <i>Some linked projects are also sharing this release. Would you like to update them ? You can select them
               and finish by clicking on "Move to this revision" button</i>
          </p>
          <p class="list-group"></p>
        </div>
        <div id="none_possible_update">
          <p>
            <i>None of the linked projects has this revision</i>
          </p>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        <button id="move_to" type="button" class="btn btn-primary">Move to this revision</button>
      </div>
    </div><!-- /.modal-content -->
  </div><!-- /.modal-dialog -->
</div><!-- /.modal -->
<!-- end update to dialog -->


<!-- start force push dialog -->
<div id="confirm_force_push_dialog" class="modal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title">It seems you are trying to push a new branch.</h4>
      </div>
      <div class="modal-body">
        Should we push also it ?
      </div>
      <div class="modal-footer">
        <button id="abort_new_branch" type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        <button id="new_branch" type="button" class="btn btn-primary">Push this new branch</button>
      </div>
    </div><!-- /.modal-content -->
  </div><!-- /.modal-dialog -->
</div><!-- /.modal -->
<!-- end new branch to dialog -->

<!-- dismiss push dialog -->
<div id="dismiss_force_push_dialog" class="modal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title">It seems you are trying to push a new head.</h4>
      </div>
      <div class="modal-body">
        We can't push new heads !<br><br> <i>you should consider carefully to push new head and solve this problem manually</i>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
      </div>
    </div><!-- /.modal-content -->
  </div><!-- /.modal-dialog -->
</div><!-- /.modal -->
<!-- end dismiss to dialog -->

% if logged_in is not None :
   ${lib.publish_project_dialog()}
% endif


<!-- nothing work -->
%if repository_error is not None:
  <div class="alert alert-danger">Sorry this repository is not available. Thanks to check configuration to solve this issue.
    You'll find bellow more technical details :
    <br>
    <br>
    <b>${repository_error}</b>
  </div>
%endif
<!-- nothing work -->

<%block name="local_js">
  <script>
    var local_project_name             = "${project.name}";
    var local_project_last_change_list = ${json.dumps(last_hundred_change_list)|n}
    var current_node                   = ${json.dumps(current_node)|n}
    var list_branches                  = ${json.dumps(list_branches)|n}
    var delivered_hash                 = ${json.dumps(delivered_hash)|n}

    $(function(){
      if(localStorage['logs_enabled']==='1'){
        $button = $('#button_log');
        display_logs($button.get(0));
      }
      $('#project_tab a').click(function (e) {
        e.preventDefault()
        $(this).tab('show')
      });
      init_my_d3(local_project_last_change_list);

     $(window).resize(function() {
        $("#d3_container > svg").attr('width',Math.floor($('#global_container').width()));
     });
    })
  </script>
</%block>


