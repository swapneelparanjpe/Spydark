// FOR EXPAND-COLLAPSE SIDENAV ON SCROLLING>>>>>>>>>>
var expand = true;
var collapse = false;
window.onscroll = function() {
    if (document.documentElement.scrollLeft > 250 && expand){
        document.getElementsByClassName('collapse-btn')[0].click();
        expand = false;
        collapse = true;
    }
    if (document.documentElement.scrollLeft < 250 && collapse){
        document.getElementsByClassName('collapse-btn')[0].click();
        expand = true;
        collapse = false;
    }
};
// <<<<<<<<<<<<<<<<<<<<<<<<<<<<<

const body = document.body;
const menuLinks = document.querySelectorAll(".admin-menu a, nav a");
const collapseBtn = document.querySelector(".admin-menu .collapse-btn");
const collapsedClass = "collapsed";

toggle_count = 0
function toggle() {
    toggle_count++;
    if (toggle_count%2 != 0) {	
        document.getElementById('dp').style.width = "30px";
        document.getElementById('dp').style.display = "block";
        document.getElementById('dp').style.marginTop = "75%";
        document.getElementById('hello').style.display = "none";
    }
    else{
        document.getElementById('dp').style.width = "60px";
        document.getElementById('dp').style.marginTop = "10%";
        document.getElementById('hello').style.display = "block";
    }
}

collapseBtn.addEventListener("click", function() {
        // toggle aria-expanded btwn TRUE and FALSE
    if (this.getAttribute("aria-expanded") == "true")
        this.setAttribute("aria-expanded", "false");
    else
        this.setAttribute("aria-expanded", "true");

        // toggle aria-label btwn COLLAPSE MENU and EXPAND MENU
    if (this.getAttribute("aria-label") == "collapse menu")
        this.setAttribute("aria-label", "expand menu");
    else
        this.setAttribute("aria-label", "collapse menu");
    body.classList.toggle(collapsedClass);
});

for (const link of menuLinks) {
    link.addEventListener("mouseenter", function() {
        body.classList.contains(collapsedClass) &&
        window.matchMedia("(min-width: 768px)").matches
        ? this.setAttribute("title", this.textContent)
        : this.removeAttribute("title");
    });
}