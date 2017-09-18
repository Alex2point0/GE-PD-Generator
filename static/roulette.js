// IFTTT Slottt Machine by Jen Hamon
// jen@ifttt.com
// github.com/jhamon

// By Oleg Khomenko

// This one is to shuffle list
Array.prototype.shuffle = function () {
  var i = this.length, j, temp;
  if (i == 0) return this;
  while (--i) {
    j = Math.floor(Math.random() * (i + 1));
    temp = this[i];
    this[i] = this[j];
    this[j] = temp;
  }
  return this;
}

// EndBy

// Vars and Constants
var wordlist1 = wordlist.slice();
wordlist1.shuffle();

var wordlist2 = wordlist.slice();
wordlist2.shuffle();

var ANIMATION_TIME = 6000;

// Functions
function buildSlotItem(text) {
  return $('<div>').addClass('slottt-machine-recipe__item')
    .text(text)
}

function buildSlotContents($container, wordlist) {
  $items = wordlist.map(buildSlotItem);
  $container.append($items);
}

function popPushNItems($container, n) {
  $children = $container.find('.slottt-machine-recipe__item');
  $children.slice(0, n).insertAfter($children.last());

  if (n === $children.length) {
    popPushNItems($container, 1);
  }
}

// After the slide animation is complete, we want to pop some items off
// the front of the container and push them onto the end. This is
// so the animation can slide upward infinitely without adding
// inifinte div elements inside the container.
function rotateContents($container, n) {
  setTimeout(function () {
    popPushNItems($container, n);
    $container.css({ top: 0 });
  }, 300);
}

function randomSlotttIndex(max) {
  var randIndex = (Math.random() * max | 0);
  return (randIndex > 10) ? randIndex : randomSlotttIndex(max);
}

function animate() {
  winners = wordlist.shuffle().slice(0, 2);

  var wordIndex = $wordbox.children().map(function (i, el) {
    return $(el).text();
  }).get().indexOf(winners[0]) + wordlist.length * 14; //Чтобы всегда крутить рулетку допустим до 140-150 элементов, если длина списка 10

  var wordIndex2 = $wordbox2.children().map(function (i, el) {
    return $(el).text();
  }).get().indexOf(winners[1]) + wordlist.length * 14; //Чтобы всегда крутить рулетку допустим до 140-150 элементов, если длина списка 10


  $wordbox.animate({ top: -wordIndex * 75 }, ANIMATION_TIME, 'swing', function () {
    rotateContents($wordbox, wordIndex);
  });

  $wordbox2.animate({ top: -wordIndex2 * 75 }, ANIMATION_TIME * 1.3, 'swing', function () {
    rotateContents($wordbox2, wordIndex2);
    $.fn.fullpage.moveSectionDown();
  });
  
  return winners; // Return Winners to store result
}


// Скрываем показывем элементы




$(function () {
  jQuery.fn.visible = function () {
    return this.css({ 'opacity': 0.0, 'visibility': 'visible' }).animate({ opacity: 1 }, 1000);
  };

  jQuery.fn.invisible = function () {
    return this.css('visibility', 'hidden');
  };


  $wordbox = $('#wordbox .slottt-machine-recipe__items_container');
  // <1> Генерируем 15 раз, чтобы можно было а) Долго крутить барабан; б) Он крутился с большой скоростью
  for (var i = 0; i < 15; i++) {
    buildSlotContents($wordbox, wordlist1);
  }

  $wordbox2 = $('#wordbox2 .slottt-machine-recipe__items_container');
  // <1> Генерируем 15 раз, чтобы можно было а) Долго крутить барабан; б) Он крутился с большой скоростью
  for (var i = 0; i < 15; i++) {
    buildSlotContents($wordbox2, wordlist2);
  }

  $("#btn-rotate").click(function () {
    $(".slottt-machine-recipe").visible(); // Можем начать показывать рулетку
    var winners = animate(); // Два победителя

    // Пишем победителей в модальное окно
    $("#section4").find("h4").html("Congratulations!"); 
    $("#section4").find("p").html(
    "<i class='fa fa-user-o'/> <b>" + winners[0] + "</b> was selected to send PD Insight to <i class='fa fa-user-o' /> <b>" + winners[1] + "</b>");
    $('#results').append("<option>" + winners[0] + " to " + winners[1] + "</option>") // Пишем победителей в список победителей
  }
  );

  // Крутим-вертим колесо
  $("img").click(function () {
    $(this).toggleClass("rotating");
  })

  // Чтобы красиво раскрывалось
  $('.search-button').click(function () {
    $(this).parent().toggleClass('open');
  });
})



