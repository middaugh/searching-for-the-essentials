var checkExist = setInterval(function() {
   if ($('#nav_links').length) {
      console.log("Exists!");
      clearInterval(checkExist);

    // Set Via URL, eg when the page is refreshed
    var navLinks = document.getElementsByClassName("nav__link");
    var currentPage = '/' + location.pathname.split("/").pop()
    console.log(currentPage);


    if (currentPage != "/"){ // If '/' then default and leaving with the set current page from index.py
        for(var i = 0; i < navLinks.length; i++){
        var url = '/' + navLinks[i].href.split('/').pop();

        if(url == currentPage) {
            console.log("setting nav__link--current on " + url)
        navLinks[i].className = "nav__link nav__link--current";
        }
        else{
            navLinks[i].className = "nav__link";
        }
    }

    }



    // Set Via Clicking -- credit to https://www.tutorialspoint.com/How-to-find-all-the-siblings-for-the-clicked-element-in-jQuery#:~:text=Front%20End%20Technology-,To%20find%20all%20the%20siblings%20for%20the%20clicked%20element%20in,class%20to%20find%20all%20siblings.
    $(".nav__link").click(function(){
         $(this).addClass("nav__link--current");
         $(this).siblings().not($(this)).removeClass("nav__link--current");
    });

   }
}, 100); // check every 100ms when page is refreshed
