<%inherit file="base.mako"/>
<%namespace name="lib" file="lib.mako"/>

% if logged_in is not None :
  <h2>
        <span class="label label-default">Dashboard</span>

        % if logged_in is not None and request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid:
        <button type="button" style="background-color:transparent;border:none" onclick="$('#new_project_dialog').modal('show');" alt="add new project">
          <span class='glyphicon glyphicon-plus' style="font-size:26px;vertical-align:bottom"></span>
        </button>
        % endif
  </h2>
  %for project in dashboard_list :
    <div class="panel panel-default node_description" data-id="${project.id}" data-update_url="${url(route_name='description',id=project.id)}">
      <div class="panel-heading">
        <h3 class="panel-title">
          <a href="${url(route_name='project_edit',id=project.id)}"><b>${project.name}</b></a>
          <i>(revision : <span class='node_description_rev'></span>)</i>
          
        </h3>
      </div>
      <div class="panel-body">
        current branch : <span class="label label-warning node_description_branch"></span
        <br>
        <br>
        current hash : <i><span class='node_description_node'></span></i>
        <br>
        current comment : <i><span class='node_description_desc'></span></i>
      </div>
    </div>
  %endfor
  %if not dashboard_list :
      > <i>The dashboard is empty</i>
  %endif

% else :

 <div class="starter-template">
   <h1>Welcome to HgDelivery webapp</h1>
   <p class="lead">The purpose of HgDelivery webapp is to allow people to deliver or manage new release easily</p>
   <br>
   <br>
   <p class="lead"><b>Please login before proceeding</b></p>
   <br>
   % if logged_in is None :
   <div>
       <form id="login_form_responsive" action="${url('login')}" method='POST'>
         <input class="span2" id="login" name="login" type="text" placeholder="your mail address">
         <input class="span2" id="password" name="password" type="password" placeholder="your password">
         <button type="submit" id="log_me" class="btn btn-primary" onclick="$('#login_form').submit()">Sign in</button>
       </form>
   </div>
 </div>

 %endif

% endif

% if logged_in is not None :
   ${lib.publish_project_dialog()}
% endif

<%block name="local_js">
  <script>init_page_overview();</script>
</%block>


