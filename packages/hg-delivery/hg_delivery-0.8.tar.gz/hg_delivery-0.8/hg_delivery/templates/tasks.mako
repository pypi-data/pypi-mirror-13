<%inherit file="base.mako"/>

<h2>All projects tasks :</h2>

<div class="tab-pane" id="tasks">
%for project in dict_project_to_tasks :
  <h3><a href="${url(route_name='project_edit',id=project.id)}">Project : ${project.name}</a></h3>
  <ul id="tasks_list">
    %for task in dict_project_to_tasks[project] :
     <li>
          <input type="text" name="task_content" value="${task.content}">
          <button data-id="${task.id}" data-url="${url(route_name='project_delete_task', id=task.id)}" onclick="delete_this_task(this)" type="button" class="btn">delete it ..</button>
          <button data-id="${task.id}" data-url="${url(route_name='project_run_task', id=task.id)}" onclick="run_this_task(this)" type="button" class="btn">run it ..</button>
     </li>
    %endfor
  </ul>
%endfor
</div>
