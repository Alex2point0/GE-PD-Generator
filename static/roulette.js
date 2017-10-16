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


// ANIMATE.CSS HELPER
$.fn.extend({
  animateCss: function (animationName) {
    var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
    this.addClass('animated ' + animationName).one(animationEnd, function () {
      $(this).removeClass('animated ' + animationName);
    });
    return this;
  }
});

// EndBy

// Vars and Constants
var wordlist1 = wordlist.slice();
wordlist1.shuffle();

var wordlist2 = wordlist.slice();
wordlist2.shuffle();

var ANIMATION_TIME = 600;

// Functions
function buildSlotItem(text) {
  return $('<div>').addClass('slottt-machine-recipe__item').text(text)
}

function generateEmailText(personFrom, personTo, time, sso) {
  // Greeting
  $("#sendEmailModal-after").find(".modal-body").find("h3").text(`Hello ${personFrom}!`);

  // Main text
  var emailBody = $("#sendEmailModal-after").find(".modal-body").find(".modal-text").html();
  emailBody = emailBody.replace("%time%", time);
  emailBody = emailBody.replace("%personTo%", personTo);

  // Update text
  $("#sendEmailModal-after").find(".modal-body").find(".modal-text").html(emailBody);

  $("#sendEmailModal").toggleClass("show");
  $("#sendEmailModal-after").toggleClass("show");

  var mailto = $("#send-email-button").attr("href");
  mailto = mailto.replace("%personTo%", personTo.replace(" ", "%20"));
  mailto = mailto.replace("%personFrom%", personFrom.replace(" ", "%20"));
  mailto = mailto.replace("%personTo%", personTo.replace(" ", "%20"));
  mailto = mailto.replace("%time%", time);

  // Update Text
  $("#send-email-button").attr("href", mailto);
}

function saveRouletteResults(form, field) {
  // only if everything is OK with SSO (9 digits)
  if (validateForm(form, field) == true) {
    // let regexPersonFrom = /^.*(?=( to ))/;
    // let regexPersonTo = / to (.*)$/;

    var personFrom = $("#personFrom").text();
    var personTo = $("#personTo").text();
    var sso = document.forms[form][field].value;
    var list_of_participants = wordlist;

    // Generate time
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1; //January is 0!
    var yyyy = today.getFullYear();
    if (dd < 10) { dd = '0' + dd; }
    if (mm < 10) { mm = '0' + mm; }
    today = mm + '/' + dd + '/' + yyyy;

    // Finally send request
    $.post('save', {
      'personFrom': personFrom,
      'personTo': personTo,
      'sso': sso,
      'time': today,
      'participants': list_of_participants
    }, generateEmailText(personFrom, personTo, today)).fail(function () { console.log("error"); })
  }

  // always return false to block submition of the form
  return false;
}


// Validate Forms
function validateForm(form, field) {
  var x = document.forms[form][field].value;

  // For SSO
  if (field == 'sso' && x.match(/^\d{9}$/)) {
    return true;
  }

  return false;
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

function animate(callback) {
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
    $("#section2").find(".container:eq(0)").hide();
    $("#section2").find(".container:eq(1)").show();
  });


  return winners; // Return Winners to store result
}


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
    $("#section3").find("h4").html("Congratulations!");
    $("#section3").find("h2").html("<i class='fa fa-user-o'/> <b>" + winners[0] + "</b><br/>was selected to send PD Insight to<br><i class='fa fa-user-o' /> <b>" + winners[1] + "</b>");
    // Пишем победителей в список победителей
    $('#results').html(`<span id="personFrom"><i class="fa fa-paper-plane-o" /> ${winners[0]}</span><br> to <br><span id="personTo"><i class="fa fa-hand-spock-o" /> ${winners[1]}</span>`);
  }
  );

  $("#btn-spinAgain").click(function () {
    $("#section2").find(".container:eq(1)").hide();
    $("#section2").find(".container:eq(0)").show();
    $("#btn-rotate").click();
  });

  // Крутим-вертим колесо
  $("img").click(function () {
    $(this).toggleClass("rotating");
  })

  // Чтобы красиво раскрывалось
  $('.search-button').click(function () {
    if ($(this).parent().hasClass("open")) {
      if ($(this).parent().find("input").attr("id") == 'participants') {

        var selectize_tags = $("#participants-selected")[0].selectize

        var participants = $(this).parent().find("input").val();
        var regex = /.*\(/;
        var participants = participants.split("; ").map(function (x) {
          if (x.match(regex)) {
            var name = x.match(regex)[0].slice(0, -1);
            return { value: name, text: name };
          }
        });

        // Add options
        selectize_tags.addOption(participants);

        // Then add this options as selected
        participants.map(function (x) { selectize_tags.addItem(x['value']) });
      }

      else {
        console.log("Don't know what to do with this input");
      }
    }

    else {
      $(this).parent().toggleClass('open');
    }
  });


  $("#btn-sendEmail").click(function () {
    $.fn.fullpage.moveSectionDown();
    $("#sendEmailModal").addClass("show");
    $("#sendEmailModal-after").removeClass("show");
  })
})
