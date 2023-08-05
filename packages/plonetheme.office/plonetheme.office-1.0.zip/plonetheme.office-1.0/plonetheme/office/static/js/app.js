$(document).foundation();
$(".select-menu-button").click(function(){
    $("ul.theme_button").slideToggle();
});
$('ul#portal-globalnav li').each(function(){
    if ($(this).attr('class')=='selected'){
        $("a.select-menu-button > span.holder").html($(' > a',this).html());	
    }
});
