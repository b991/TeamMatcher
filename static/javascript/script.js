//applied on /grid to change the drop down option of viewing profiles
const expand_down_btn = document.getElementById("expand_down");
const hidden_questions = document.getElementById("hidden_list");
const expand_up_btn = document.getElementById("expand_up");

expand_down_btn.addEventListener("click",()=>{
    hidden_questions.classList.toggle("hidden");
    expand_down_btn.classList.toggle("hidden");
    expand_up_btn.classList.toggle("hidden");

});

expand_up_btn.addEventListener("click", () => {
  hidden_questions.classList.toggle("hidden");
  expand_up_btn.classList.toggle("hidden");
  expand_down_btn.classList.toggle("hidden");

});

function Change_star_icon(ele) {
    ele.classList.toggle("fill-yellow-600")
}






