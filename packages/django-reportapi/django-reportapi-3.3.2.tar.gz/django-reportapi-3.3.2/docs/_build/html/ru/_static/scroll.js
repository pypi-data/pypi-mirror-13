/* интеллектуальная прокрутка содержимого sidebar */

function scrollSidebar() {

    if (!$('#sidebar:visible').size()) return;

    var sb = $('.sphinxsidebarwrapper'),
        win = $(window),
        sbh = sb.height(),
        offset = $('.sphinxsidebar').position()['top'],
        wintop = win.scrollTop(),
        winbot = wintop + win.innerHeight(),
        curtop = sb.position()['top'],
        curbot = curtop + sbh;

    // sidebar помещается в окно?
    if (sbh < win.innerHeight()) {
        // да: простой случай - всегда держать вверху
        sb.css('top', $u.min([$u.max([0, wintop - offset - 10]),
                                $(document).height() - sbh - 200]));
    } else {
        // нет: прокручиваем только если верхний/нижний край
        // боковой панели на верхнем/нижнем краю окна
        if (curtop > wintop && curbot > winbot) {
            sb.css('top', $u.max([wintop - offset - 10, 0]));
        } else if (curtop < wintop && curbot < winbot) {
            sb.css('top', $u.min([winbot - sbh - offset - 20,
                                  $(document).height() - sbh - 200]));
        }
    }
}

$(document).ready(function($) { $(window).scroll(scrollSidebar); });

