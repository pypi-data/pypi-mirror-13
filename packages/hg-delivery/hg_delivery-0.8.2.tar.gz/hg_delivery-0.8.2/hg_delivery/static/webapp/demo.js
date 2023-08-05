function main() {
  var db = new Kinto({remote: "http://127.0.0.1:8888/v1"});
  var tasks = db.collection("tasks");

  document.getElementById("form")
    .addEventListener("submit", function(event) {
      event.preventDefault();
      tasks.create({
        title: event.target.title.value,
        done: false
      })
      .then(function(res) {
        event.target.title.value = "";
        event.target.title.focus();
      })
      .catch(function(err) {
        console.error(err);
      });
    });

  console.log('ocuocuu 1');
  document.getElementById("clearCompleted")
    .addEventListener("click", function(event) {
      event.preventDefault();
      console.log('ocuocuu');
      tasks.list()
        .then(function(res) {
          console.log('ocuocuu2');
          // Filter tasks according to their done status
          var completed = res.data.filter(function(task) {
            console.log('ocuocuu3');
            return task.done;
          });
          // Delete all completed tasks
          return Promise.all(completed.map(function(task) {
            console.log('deleting task'+task.id);
            return tasks.delete(task.id);
          }));
        })
        .then(render)
        .catch(function(err) {
          console.error(err);
        });
    });

  document.getElementById("sync")
    .addEventListener("click", function(event) {
      event.preventDefault();
      tasks.sync({headers: {Authorization: "Basic " + btoa("user:pass")}})
        .then(function(res) {
          document.getElementById("results").value = JSON.stringify(res, null, 2);
        })
        .then(render)
        .catch(function(err) {
          console.error(err);
        });
    });

  function renderTask(task) {
    var li = document.createElement("li");
    li.classList.add("list-group-item");
    li.innerHTML = task.title;
    return li;
  }

  function renderTasks(tasks) {
    var ul = document.getElementById("tasks");
    ul.innerHTML = "";
    tasks.forEach(function(task) {
      ul.appendChild(renderTask(task));
    });
  }

  function render() {
    tasks.list().then(function(res) {
      renderTasks(res.data);
    })
    .catch(function(err) {
      console.error(err);
    });
  }

  render();

}

window.addEventListener("DOMContentLoaded", main);
