 /* open side navigation menu */

 function openNav(nav) {

    /* get list of all side navigation menues */
    var active = document.getElementsByClassName('sidenav');

    /* iterated through all side nav menues */
    for (let i = 0; i < active.length; i++) {
        /* check if menu i is active */
        if (active[i].style.width == "250px") {
            /* if side nav is active, close side nav */
            active[i].style.width = "0";
        }
    }


    document.getElementById(nav).style.width = "250px";
    /* document.body.style.backgroundColor = "rgba(0,0,0,0.4)"; */
}


/* close side navigation menu */

function closeNav(nav) {
    document.getElementById(nav).style.width = "0";
    /* document.body.style.backgroundColor = "white"; */
}