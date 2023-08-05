<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    % if logged_in is not None :
    <title>Hg Delivery 1.0 welcome :)</title>
    % else :
    <title>Hg Delivery 1.0</title>
    % endif :

    <!-- Bootstrap -->
    <link href="${request.static_url('hg_delivery:static/bootstrap-3.1.1/css/bootstrap.css')}" rel="stylesheet">
    <link href="${request.static_url('hg_delivery:static/delivery.css')}" rel="stylesheet">
    <link href="${request.static_url('hg_delivery:static/codemirror.css')}" rel="stylesheet">
    <link href="${request.static_url('hg_delivery:static/mergely.css')}" rel="stylesheet">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>

    <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          % if logged_in is not None :
            <a class="navbar-brand" href="/">Dashboard</a>
          % else :
            <a class="navbar-brand" href="/">HgDelivery</a>
          % endif :
        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li><a href="${url('contact')}">Contact</a></li>
             % if logged_in is not None and request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid:
              <li><a href="${url('users')}">Users</a></li>
              <li><a href="${url('tasks')}">Tasks</a></li>
              % if project is UNDEFINED and request.url == request.route_url('home'):
                <li><a href="#" onclick="$('#new_project_dialog').modal('show');">Add a new project</a></li>
              % endif
             % endif

             % if logged_in is not None :
               <li><a id="sign_out" href="${url('logout')}">Sign out</a></li>
             % endif

             % for __project in projects_list :
               <li><a class="project_link responsive_link" href="${url(route_name='project_edit',id=__project.id)}">${__project.name}</a></li>
             % endfor
          </ul>
          % if logged_in is not None :
            <form name="view_project" class="navbar-form pull-right">
               % if projects_list :
                 <!-- Single button for project management-->
                 <div class="btn-group">
                   <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                     % if project is not UNDEFINED:
                       <span id="project_name">${project.name}</span> <span class="caret"></span>
                     % else :
                       Projects (<span id="project_number">${len(projects_list)}</span>)<span class="caret"></span>
                     % endif
                   </button>
                   <ul id="projects_list" class="dropdown-menu" role="menu" data-url="${url(route_name='project_edit',id='')}">
                   % for __project in projects_list :
                     <li><a class="project_link" href="${url(route_name='project_edit',id=__project.id)}">${__project.name}</a></li>
                   % endfor
                   % if (project is UNDEFINED and request.url == request.route_url('home')) or project is not UNDEFINED:
                     <li class="divider"></li>
                     <li><a href="#" onclick="$('#new_project_dialog').modal('show');">Add a new project</a></li>
                    % endif
                   </ul>
                 </div>
               % else :
                 <!-- Single button for project management-->
                 <div class="btn-group" style="display:none">
                   <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                       Projects (<span id="project_number">0</span>) <span class="caret"></span>
                   </button>
                   <ul id="projects_list" class="dropdown-menu" role="menu" data-url="${url(route_name='project_edit',id='')}">
                   </ul>
                 </div>
               % endif

               % if project is not UNDEFINED :
               <!-- Single button for project management-->
               <div class="btn-group" style="margin-left:20px">
                 <button id="manage_project" type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" style="min-width:80px">
                   Manage project <span class="caret"></span>
                 </button>
                 <ul class="dropdown-menu" role="menu">
                   <li><a href="#" onclick="$('#edit_project_dialog').modal('show');">Edit properties</a></li>
                   <li class="divider"></li>
                   <li><a id="view_delete_project" href="#" onclick="delete_this_project()" data-url="${url(route_name='project_delete',id=project.id)}">Delete</a></li>
                 </ul>
                 <button type="button" class="btn btn-default" id="button_log" style="margin-left:10px" id="logs" onclick="display_logs(this);" data-url="${url(route_name='project_logs',id=project.id)}">
                   Logs
                 </button>
               </div>
               % endif

            </form>
          % endif
          % if logged_in is None :
            <form id="login_form" class="navbar-form pull-right" action="${url('login')}" method='POST'>
              <input class="span2" id="login" name="login" type="text" placeholder="your mail address">
              <input class="span2" id="password" name="password" type="password" placeholder="your password">
              <button type="submit" id="log_me" class="btn btn-primary" onclick="$('#login_form').submit()">Sign in</button>
            </form>
          %endif
        </div><!--/.nav-collapse -->
      </div>
    </div>

    <!-- STARTING/ .container -->
    <div id="global_container" class="container">
      ${self.body()}
    </div>
    <!-- ENDING/ .container -->

    % if project is not UNDEFINED :
    <div id="container_logs" style="display:none">
      <button type="button" class="close" onclick="display_logs($('#button_log').get(0));" aria-hidden="true" style="font-size:33px">&times;</button>
      <div id='logs'>
      </div>
    </div>
    % endif

    <div id="container_alert">
    </div>

    <!-- STARTING/ GLOBAL SCRIPT -->
    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="${request.static_url('hg_delivery:static/jquery-1.11.1.min.js')}"></script>
    <script src="${request.static_url('hg_delivery:static/delivery.js')}"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="${request.static_url('hg_delivery:static/bootstrap-3.1.1/js/bootstrap.min.js')}"></script>
    <script src="${request.static_url('hg_delivery:static/codemirror.min.js')}"></script>
    <script src="${request.static_url('hg_delivery:static/searchcursor.js')}"></script>
    <script src="${request.static_url('hg_delivery:static/mergely.min.js')}"></script>
    <script src="${request.static_url('hg_delivery:static/d3.v3.min.js')}" charset="utf-8"></script>
    <!-- ENDING/ GLOBAL SCRIPT -->
    
    <%block name="local_js">
    <!-- define local script ... -->
    </%block>
  </body>
</html>
