<%!
  import json
  import os.path
%>
<%inherit file="base.mako"/>
<a href="${url(route_name='project_edit',id=project.id)}">back to project</a>

<div id="overview" class="panel panel-default" style="margin:10px 10px">
  % if diff.lst_files :
    <div class="panel panel-default col-md-3" style="margin:10px;padding-left:0px;padding-right:0px;">
      <div class="panel-heading">
        <h3 class="panel-title">Files</h3>
      </div>
      <div class="panel-body">
         <div id="files" class="list-group">
           %for i, file in enumerate(diff.lst_files) :
             <a href="#" class="list-group-item" onclick="$('div[id^=file_]').hide();$('#file_${i}').show()">${os.path.basename(file)}</a>
           %endfor
         </div>
      </div>
    </div>
  % endif
  <div class="panel-body">
  % if diff.raw_diff :
    % for i, file in enumerate(diff.lst_files) :
      % if file in diff.dict_files :
       <div id="file_${i}" style="display:none">
          ${diff.dict_files[file] |n}
       </div>
      % endif
    % endfor
  % else :
    <p class="bg-info">
      <br>
      &nbsp;  No diff is available for this revision
      <br>
      <br>
    </p>
  % endif
  </div>
</div>
