<%inherit file="base.mako"/>
<%namespace name="lib" file="lib.mako"/>

 <div class="starter-template">
   <h1>HgDelivery main repository is on <a href="http://bitbucket.org/tuck/hg_delivery">bitbucket.org</a></h1>
   <p class="lead"></p>
 </div>

 % if logged_in is not None :
    ${lib.publish_project_dialog()}
 % endif

