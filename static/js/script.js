const addStudentBtn = document.getElementById("addStudentBtn");
const startAddingBtn = document.getElementById("startAddingBtn");

if (addStudentBtn) {
  addStudentBtn.addEventListener("click", function () {
    window.location.href = "/add-student";
  });
}

if (startAddingBtn) {
  startAddingBtn.addEventListener("click", function () {
    window.location.href = "/add-student";
  });
}
